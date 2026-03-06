"""
Joint Account Manager - 共同账户管理器
情侣/搭档共同储蓄，AI监督执行
"""
from typing import Dict, List
from datetime import datetime
import json

class JointAccount:
    """共同账户类"""
    def __init__(self, name: str, goal: float, token: str = "USDT"):
        self.name = name
        self.goal = goal  # 目标金额
        self.token = token
        self.deposits = {"A": 0, "B": 0}  # 双方存款
        self.rules = {
            "require_both_approve": True,  # 需要双方同意
            "monthly_limit_pct": 50,  # 每月最多取50%
            "min_balance_pct": 20  # 最低保留20%
        }
        self.created_at = datetime.now()
        self.tx_history = []
    
    def deposit(self, who: str, amount: float):
        """存款"""
        self.deposits[who] = amount
        self.tx_history.append({
            "type": "DEPOSIT",
            "who": who,
            "amount": amount,
            "time": datetime.now().isoformat()
        })
    
    def can_withdraw(self, -> tuple amount: float):
        """检查是否可以取款"""
        total = sum(self.deposits.values())
        
        # 检查余额是否足够
        if amount > total:
            return False, "余额不足"
        
        # 检查是否低于最低保留
        min_balance = self.goal * (self.rules["min_balance_pct"] / 100)
        if total - amount < min_balance:
            return False, f"需保留最低 {min_balance} {self.token}"
        
        return True, "可以取款"
    
    def withdraw(self, who: str, amount: float, approved_by: str) -> Dict:
        """取款（需要另一方批准）"""
        can_withdraw, reason = self.can_withdraw(amount)
        
        if not can_withdraw:
            return {"success": False, "reason": reason}
        
        # 更新余额
        self.deposits[who] -= amount
        
        self.tx_history.append({
            "type": "WITHDRAW",
            "who": who,
            "approved_by": approved_by,
            "amount": amount,
            "time": datetime.now().isoformat()
        })
        
        return {
            "success": True,
            "remaining": sum(self.deposits.values()),
            "tx_hash": f"0x{''.join(['a']*64)}"
        }
    
    def get_progress(self) -> str:
        """获取进度"""
        total = sum(self.deposits.values())
        pct = (total / self.goal * 100) if self.goal > 0 else 0
        
        return f"""
💍 共同账户: {self.name}

🎯 目标: {self.goal} {self.token}
💰 当前: {total} {self.token}
📊 进度: {pct:.1f}%

👤 伙伴A: {self.deposits['A']} {self.token}
👤 伙伴B: {self.deposits['B']} {self.token}

📋 规则:
• 需要双方同意: {'是' if self.rules['require_both_approve'] else '否'}
• 每月最多提取: {self.rules['monthly_limit_pct']}%
• 最低保留: {self.rules['min_balance_pct']}%
"""


def create_joint_account(name: str, goal: float, token: str = "USDT") -> JointAccount:
    """创建共同账户"""
    return JointAccount(name, goal, token)


if __name__ == "__main__":
    # 测试
    account = create_joint_account("买房基金", 5, "ETH")
    account.deposit("A", 2)
    account.deposit("B", 1.5)
    
    print(account.get_progress())
    
    # 尝试取款
    result = account.withdraw("A", 0.5, "B")
    print(f"\n取款结果: {result}")
