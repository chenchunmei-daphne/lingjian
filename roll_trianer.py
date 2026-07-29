import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
import os

class SelfComposingDualModeTransformerModel(nn.Module):
    """增强版：支持输出层参数复用"""
    
    def __init__(self, in_ft=3264, center_ft=800, in_rx=514, center_rx=514, ffn=514, heads=2, 
                 output_f=3264, output_rx=256, output_tx=1, dropout=0.01, softmax=True, bias=False,
                 divided_d=True, linformer=False, k=128, l=1):
        super().__init__()
        
        self.output_rx = output_rx
        self.output_tx = output_tx
        self.output_f = output_f
        self.l = l
        self.center_rx = center_rx
        self.center_ft = center_ft
        
        # 编码器
        self.con1d0 = nn.Sequential(
            nn.Conv1d(in_ft, center_ft * 2, kernel_size=1, bias=False),
            nn.BatchNorm1d(center_ft * 2), nn.GELU(),
            nn.Conv1d(center_ft * 2, center_ft * 2, kernel_size=3, padding=1, groups=center_ft * 2, bias=False),
            nn.BatchNorm1d(center_ft * 2), nn.GELU(),
            nn.Conv1d(center_ft * 2, center_ft, kernel_size=1, bias=False)
        )
        
        self.linear0 = nn.Linear(in_rx, center_rx, bias=bias)
        
        # 主干网络（单个可复用块）
        self.backbone = nn.Sequential(nn.Linear(center_rx, center_rx, bias=bias), 
                                      nn.Linear(center_rx, center_rx, bias=bias))                                      
        
        # 解码器
        self.con1d1 = nn.Sequential(
            nn.Conv1d(center_ft, center_ft, kernel_size=3, padding=1, groups=center_ft, bias=False),
            nn.BatchNorm1d(center_ft), nn.GELU(),
            nn.Conv1d(center_ft, output_f, kernel_size=1, bias=bias))
        
        self.linear_real = nn.Linear(center_rx, output_rx * output_tx, bias=bias)
        self.linear_imag = nn.Linear(center_rx, output_rx * output_tx, bias=bias)
        
        self.dropout = nn.Dropout(dropout)
        
        self._init_weights()
    
    def _init_weights(self):
        nn.init.trunc_normal_(self.linear_real.weight, mean=0.0, std=0.01)
        nn.init.trunc_normal_(self.linear_imag.weight, mean=0.0, std=0.01)
        if self.linear_real.bias is not None:
            nn.init.constant_(self.linear_real.bias, 0.0)
            nn.init.constant_(self.linear_imag.bias, 0.0)
    
    def set_l(self, l):
        self.l = l
    
    def forward(self, x, return_attention=False):
        batch_size = x.shape[0]
        
        x = self.linear0(self.con1d0(x))  # 输入层
        
        # 自组合 (G ∘)^l
        attention_weights_list = []
        for _ in range(self.l):
            if return_attention:
                x = self.backbone(x)
                # attention_weights_list.append(attn_weights)
            else:
                x = self.backbone(x)

        # 输出层
        x = self.con1d1(x)
        x_real = self.linear_real(x)
        x_imag = self.linear_imag(x)
        
        x_real = x_real.reshape(batch_size, self.output_f, self.output_tx, self.output_rx)
        x_imag = x_imag.reshape(batch_size, self.output_f, self.output_tx, self.output_rx)
        
        x_complex = torch.complex(x_real, x_imag)
        
        if return_attention:
            return x_complex, attention_weights_list
        return x_complex
    



def generate_dummy_data(batch_size, in_ft=3264, in_rx=514):
    """
    生成随机复数数据作为输入和输出
    
    Returns:
        x: 输入复数张量 (batch_size, in_ft, in_rx)
        y: 输出复数张量 (batch_size, output_f, output_tx, output_rx)
    """
    # 生成复数输入
    x_real = torch.randn(batch_size, in_ft, in_rx)
    x_imag = torch.randn(batch_size, in_ft, in_rx)
    x = torch.complex(x_real, x_imag)
    return x


def train_one_epoch(model, optimizer, criterion, num_batches=3, batch_size=16, device='cpu'):
    """
    训练一个epoch
    
    Args:
        model: 模型
        optimizer: 优化器
        criterion: 损失函数
        num_batches: 每个epoch的batch数量
        batch_size: batch大小
        device: 设备
    
    Returns:
        avg_loss: 平均损失
    """
    model.train()
    total_loss = 0.0
    
    for batch_idx in range(num_batches):
        # 生成随机数据
        x = generate_dummy_data(batch_size)
        x_real = x.real
        x_imag = x.imag
        
        # 将输入转换为实数张量（模型期望实数输入）
        # 根据您的模型，输入是 (batch, in_ft, in_rx) 的实数
        # 这里假设模型输入是实数，我们将实部和虚部拼接或分别处理
        # 但根据您原始的NewDualModeTransformerModel，输入是实数
        # 所以我们只使用实部作为输入
        x_input = x_real.to(device)  # (batch, in_ft, in_rx)
        
        # 前向传播
        optimizer.zero_grad()
        output = model(x_input)  # (batch, output_f, output_tx, output_rx) 复数
        
        # 生成随机目标（与输出形状匹配）
        y_real = torch.randn(output.shape, device=device)
        y_imag = torch.randn(output.shape, device=device)
        y_target = torch.complex(y_real, y_imag)
        
        # 计算损失（使用复数MSE或实部虚部分别计算）
        loss_real = criterion(output.real, y_target.real)
        loss_imag = criterion(output.imag, y_target.imag)
        loss = loss_real + loss_imag
        
        # 反向传播
        loss.backward()
        optimizer.step()
        
        total_loss += loss.item()
        print(f"    Batch {batch_idx + 1}/{num_batches}, Loss: {loss.item():.6f}")
    
    avg_loss = total_loss / num_batches
    return avg_loss


def train_step1():
    """
    第一步训练：浅层模型 (l=1, output_f=1)
    """
    print("=" * 60)
    print("Step 1: Training shallow model with l=1, output_f=1")
    print("=" * 60)
    
    # 设置设备
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"Using device: {device}")
    
    # 创建模型
    model_1 = SelfComposingDualModeTransformerModel(
        output_f=1,  # 输出频率维度为1
        l=1          # 组合深度为1
    )
    model_1 = model_1.to(device)
    
    # 打印参数量
    total_params = sum(p.numel() for p in model_1.parameters())
    trainable_params = sum(p.numel() for p in model_1.parameters() if p.requires_grad)
    print(f"Model parameters: Total={total_params:,}, Trainable={trainable_params:,}")
    print(f"Model config: l={model_1.l}, output_f={model_1.output_f}")
    
    # 设置优化器和损失函数
    optimizer = optim.Adam(model_1.parameters(), lr=1e-3)
    criterion = nn.MSELoss()
    
    # 训练1个epoch
    print("\nStarting training...")
    for epoch in range(1, 2):  # 1个epoch
        print(f"\nEpoch {epoch}:")
        avg_loss = train_one_epoch(
            model=model_1,
            optimizer=optimizer,
            criterion=criterion,
            num_batches=3,
            batch_size=16,
            device=device
        )
        print(f"  Average Loss: {avg_loss:.6f}")
    
    # 保存模型
    save_path = "model_l1_outputf1.pth"
    torch.save(model_1.state_dict(), save_path)
    print(f"\nModel saved to: {save_path}")
    print("=" * 60)
    
    return model_1, save_path


def train_step2(model_1_path="model_l1_outputf1.pth"):
    """
    第二步训练：深层模型 (l=2, output_f=4)，复用第一步的参数
    """
    print("\n" + "=" * 60)
    print("Step 2: Extending to deeper model with l=2, output_f=4")
    print("=" * 60)
    
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"Using device: {device}")
    
    if not os.path.exists(model_1_path):
        raise FileNotFoundError(f"Model file not found: {model_1_path}")
    print(f"Loading model from: {model_1_path}")
    
    # 创建深层模型
    model_2 = SelfComposingDualModeTransformerModel(
        output_f=4,  # 输出频率维度扩展到4
        l=2          # 组合深度增加到2
    )
    model_2 = model_2.to(device)
    
    print(f"Model config: l={model_2.l}, output_f={model_2.output_f}")
    print(f"Model 2 linear_real output features: {model_2.linear_real.out_features}")
    
    # ===== 加载并复用第一步的参数 =====
    print("\nLoading and transferring weights from step 1...")
    
    state_dict_1 = torch.load(model_1_path, map_location=device)
    model_2_state = model_2.state_dict()
    
    # ===== 处理 con1d1 的输出通道扩展 =====
    # con1d1 结构: 
    #   0: Conv1d(center_ft, center_ft, kernel_size=3, padding=1, groups=center_ft)
    #   1: BatchNorm1d(center_ft)
    #   2: GELU()
    #   3: Conv1d(center_ft, output_f, kernel_size=1)  <-- 这是输出层
    
    old_conv_weight = state_dict_1['con1d1.3.weight']  # (1, 800, 1)
    new_conv_weight = old_conv_weight.repeat(4, 1, 1)   # (4, 800, 1)
    model_2_state['con1d1.3.weight'] = new_conv_weight
    print(f"  con1d1.3.weight: {old_conv_weight.shape} -> {new_conv_weight.shape}")
    
    # ===== linear_real 和 linear_imag 保持相同形状 =====
    # 注意：linear_real/imag 的输出维度是 output_rx * output_tx，与 output_f 无关
    # 所以直接复制即可
    # model_2_state['linear_real.weight'] = state_dict_1['linear_real.weight'].clone()
    # model_2_state['linear_imag.weight'] = state_dict_1['linear_imag.weight'].clone()
    # print(f"  linear_real.weight: {state_dict_1['linear_real.weight'].shape} (unchanged)")
    # print(f"  linear_imag.weight: {state_dict_1['linear_imag.weight'].shape} (unchanged)")
    
    # ===== 复用其他参数（编码器和主干网络） =====
    reused_count = 0
    print("\nReusing encoder and backbone weights:")
    for name, param in state_dict_1.items():
        # 跳过已经处理过的输出层
        if name.startswith('con1d1'):
            continue
        
        # 检查参数是否存在且形状匹配
        if name in model_2_state and param.shape == model_2_state[name].shape:
            model_2_state[name] = param.clone()
            reused_count += 1
            print(f"  Reused: {name}")
        elif name in model_2_state and param.shape != model_2_state[name].shape:
            print(f"  Shape mismatch for {name}: {param.shape} vs {model_2_state[name].shape}")
    
    # 加载参数
    model_2.load_state_dict(model_2_state)
    print(f"\nReused {reused_count} layers from step 1 model")
    
    # ===== 继续训练深层模型 =====
    # 使用较小的学习率进行微调
    optimizer = optim.Adam(model_2.parameters(), lr=1e-4)
    criterion = nn.MSELoss()
    
    print("\nStarting fine-tuning of deeper model...")
    for epoch in range(1, 2):  # 1个epoch
        print(f"\nEpoch {epoch}:")
        avg_loss = train_one_epoch(
            model=model_2,
            optimizer=optimizer,
            criterion=criterion,
            num_batches=3,
            batch_size=16,
            device=device
        )
        print(f"  Average Loss: {avg_loss:.6f}")
    
    # 保存深层模型
    save_path = "model_l2_outputf4.pth"
    torch.save(model_2.state_dict(), save_path)
    print(f"\nModel saved to: {save_path}")
    print("=" * 60)
    
    return model_2

# model = SelfComposingDualModeTransformerModel(output_f=1, l=1)
# state_dict = model.state_dict()

# print("All keys in state_dict:")
# for key in state_dict.keys():
#     print(f"  {key}")
# exit()
# model_1, model_1_path = train_step1()

model_1_path = "model_l1_outputf1.pth"
model_2 = train_step2(model_1_path)

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
dummy_input = torch.randn(2, 3264, 514).to(device)

with torch.no_grad():
    # 重新加载模型1进行测试（如果有的话）
    if os.path.exists(model_1_path):
        model_1 = SelfComposingDualModeTransformerModel(output_f=1, l=1).to(device)
        model_1.load_state_dict(torch.load(model_1_path, map_location=device))
        out1 = model_1(dummy_input)
        print(f"Model 1 (l=1, output_f=1) output shape: {out1.shape}")
    
    # 测试模型2
    out2 = model_2(dummy_input)
    print(f"Model 2 (l=2, output_f=4) output shape: {out2.shape}")

print("\n" + "=" * 60)
print("SECOND ITERATION COMPLETED SUCCESSFULLY!")
print("=" * 60)
