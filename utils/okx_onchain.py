"""
OKX OnchainOS Integration
Connect to OKX for 0% fee trading and Smart Money signals
"""
import os
import requests
import json
from typing import Dict, List, Optional

# OKX API Configuration
OKX_API_KEY = os.getenv("OKX_API_KEY", "")
OKX_SECRET = os.getenv("OKX_SECRET_KEY", "")
OKX_PASSPHRASE = os.getenv("OKX_PASSPHRASE", "")
OKX_BASE_URL = "https://www.okx.com"

def get_headers(endpoint: str, method: str = "GET") -> Dict:
    """Generate OKX API headers"""
    import hmac
    import base64
    import time
    
    timestamp = str(int(time.time()))
    prehash = timestamp + method + endpoint
    
    if OKX_SECRET:
        mac = hmac.new(OKX_SECRET.encode(), prehash.encode(), digestmod='sha256')
        signature = base64.b64encode(mac.digest()).decode()
        
        headers = {
            "Content-Type": "application/json",
            "OKX-ACCESS-KEY": OKX_API_KEY,
            "OKX-ACCESS-SIGN": signature,
            "OKX-ACCESS-TIMESTAMP": timestamp,
            "OKX-ACCESS-PASSPHRASE": OKX_PASSPHRASE
        }
    else:
        headers = {"Content-Type": "application/json"}
    
    return headers

def get_token_price(chain: str, token_address: str) -> Optional[Dict]:
    """Get token price from OKX DEX aggregator"""
    try:
        # Use OKX price API
        url = f"{OKX_BASE_URL}/api/v5/market/token-dex-price"
        params = {
            "chainIndex": _get_chain_index(chain),
            "tokenAddress": token_address
        }
        
        resp = requests.get(url, params=params, headers=get_headers("/api/v5/market/token-dex-price"))
        
        if resp.status_code == 200:
            data = resp.json()
            if data.get("code") == "0":
                return data["data"][0]
        
        return None
    except:
        return None

def _get_chain_index(chain: str) -> str:
    """Map chain name to OKX chain index"""
    chains = {
        "ethereum": "1",
        "solana": "501",
        "bsc": "56",
        "base": "8453"
    }
    return chains.get(chain.lower(), "1")

def get_dex_quote(chain: str, from_token: str, to_token: str, amount: float) -> Optional[Dict]:
    """Get DEX quote (0% fee)"""
    try:
        url = f"{OKX_BASE_URL}/api/v5/dex/aggregator/quote"
        params = {
            "chainIndex": _get_chain_index(chain),
            "fromTokenAddress": from_token,
            "toTokenAddress": to_token,
            "amount": str(amount),
            "slippage": "1"
        }
        
        resp = requests.get(url, params=params, headers=get_headers("/api/v5/dex/aggregator/quote"))
        
        if resp.status_code == 200:
            data = resp.json()
            if data.get("code") == "0":
                return data["data"][0]
        
        return None
    except

def build_swap:
        return None_tx(chain: str, from_token: str, to_token: str, amount: float, 
                  recipient: str) -> Optional[Dict]:
    """Build swap transaction (for signless trading)"""
    quote = get_dex_quote(chain, from_token, to_token, amount)
    
    if not quote:
        return None
    
    try:
        url = f"{OKX_BASE_URL}/api/v5/dex/aggregator/swap"
        data = {
            "chainIndex": _get_chain_index(chain),
            "fromTokenAddress": from_token,
            "toTokenAddress": to_token,
            "amount": str(amount),
            "slippage": "1",
            "userWalletAddress": recipient
        }
        
        resp = requests.post(url, json=data, headers=get_headers("/api/v5/dex/aggregator/swap", "POST"))
        
        if resp.status_code == 200:
            result = resp.json()
            if result.get("code") == "0":
                return result["data"][0]
        
        return None
    except:
        return None

def get_smart_money_signals(chain: str = "solana") -> List[Dict]:
    """
    Get Smart Money buy signals from OKX
    This is a simplified version - the actual API requires subscription
    """
    # Simulated Smart Money data
    # In production, use OKX Signal API
    
    signals = [
        {
            "chain": "solana",
            "token": "DEEP",
            "token_address": "EPjFWdd5AufqSSqeM2qNUtxnuPW4K2Kq9x",
            "wallet": "7xKXtg2CW87d97TXJSDpbD5jBkheTqA83TZRuJosgAsU",
            "action": "BUY",
            "amount": 25000,
            "amount_usd": 125000,
            "tx_hash": "5x7...",
            "time": "2 min ago",
            "source": "Smart Money"
        },
        {
            "chain": "solana",
            "token": "DRGON", 
            "token_address": "EpX5r1u6KfkzjG1Q6eBzYwQg3aVjT6tF1Y",
            "wallet": "9xQeWvG816bVc9AAQqn3HPg7uHQ5r7Y3r",
            "action": "BUY",
            "amount": 15000,
            "amount_usd": 82000,
            "tx_hash": "3k9...",
            "time": "5 min ago",
            "source": "Whale"
        },
        {
            "chain": "solana",
            "token": "KURO",
            "token_address": "2sX5r1u6KfkzjG1Q6eBzYwQg3aVjT6tF1Y",
            "wallet": "GK2...abc",
            "action": "BUY",
            "amount": 8000,
            "amount_usd": 45000,
            "tx_hash": "8f2...",
            "time": "12 min ago",
            "source": "KOL"
        }
    ]
    
    return signals

def get_signals_report(chain: str = "solana", min_amount: int = 10000) -> str:
    """Generate signals report"""
    signals = get_smart_money_signals(chain)
    
    # Filter by amount
    filtered = [s for s in signals if s["amount_usd"] >= min_amount]
    
    if not filtered:
        return f"❌ 没有找到超过 ${min_amount} 的信号"
    
    msg = f"🐋 *Smart Money 信号*\n\n"
    
    for s in filtered:
        emoji = "🟢" if s["action"] == "BUY" else "🔴"
        source_emoji = {"Smart Money": "🧠", "Whale": "🐋", "KOL": "📢"}.get(s["source"], "📊")
        
        msg += f"{source_emoji} *{s['source']}*\n"
        msg += f"   代币: {s['token']}\n"
        msg += f"   {emoji} {s['action']} ${s['amount_usd']:,}\n"
        msg += f"   时间: {s['time']}\n\n"
    
    msg += "💡 输入 /copy 执行跟单"
    
    return msg

def get_swap_estimate(chain: str, from_token: str, to_token: str, amount: float) -> str:
    """Get swap estimate with 0% fee"""
    quote = get_dex_quote(chain, from_token, to_token, amount)
    
    if not quote:
        return "❌ 无法获取报价"
    
    msg = f"💱 *兑换预览 (0% 服务费)*\n\n"
    msg += f"从: {amount} {from_token}\n"
    msg += f"到: ~{quote.get('toAmount', 'N/A')} {to_token}\n"
    msg += f"滑点: 1%\n"
    msg += f"路由器: OKX DEX Aggregator\n\n"
    msg += "⚡ 确认后一步完成授权+兑换"
    
    return msg

def simulate_signless_swap(chain: str, from_token: str, to_token: str, 
                           amount: float, recipient: str) -> str:
    """Simulate signless swap (approve + swap in one)"""
    tx = build_swap_tx(chain, from_token, to_token, amount, recipient)
    
    if not tx:
        return "❌ 构建交易失败"
    
    msg = f"✅ *交易已构建*\n\n"
    msg += f"链: {chain.upper()}\n"
    msg += f"从: {amount} {from_token}\n"
    msg += f"到: {to_token}\n\n"
    msg += "🔄 签名后自动执行 (免签名模式)"
    
    return msg


if __name__ == "__main__":
    # Test
    print(get_signals_report("solana", 10000))
    print("\n" + "="*50 + "\n")
    print(get_swap_estimate("solana", "SOL", "USDC", 1))
