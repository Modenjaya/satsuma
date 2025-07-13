from web3 import Web3
from dotenv import load_dotenv
import asyncio
import random
import time
import sys
import os
import json
from rich.console import Console
from rich.table import Table

# Initialize rich console
console = Console()

# Load environment variables
load_dotenv()

# File to store persistent transaction count
CONFIG_FILE = "satsuma_config.json"

# === Animated Banner ===
def display_banner():
    banner_text = """
███████╗ █████╗ ████████╗███████╗██╗   ██║███╗   ███╗ █████╗ 
██╔════╝██╔══██╗╚══██╔══╝██╔════╝██║   ██║████╗ ████║██╔══██╗
███████╗███████║   ██║   ███████╗██║   ██║██╔████╔██║███████║
╚════██║██╔══██║   ██║   ╚════██║██║   ██║██║╚██╔╝██║██╔══██║
███████║██║  ██║   ██║   ███████║╚██████╔╝██║ ╚═╝ ██║██║  ██║
╚══════╝╚═╝  ╚═╝   ╚═╝   ╚══════╝ ╚═════╝ ╚═╝     ╚═╝╚═╝  ╚═╝
    """
    console.print(f"[bold cyan]{banner_text}[/bold cyan]", justify="center")
    console.print(f"[bold green]L E T S - F U C K - T H I S - T E S T N E T [/bold green]", justify="center")
    console.print("-" * 50, style="green", justify="center")
    for _ in range(3):
        console.print(f"[yellow]> Initializing{'.' * (_ % 4)}[/yellow]", justify="center", end="\r")
        time.sleep(0.3)
    console.print(" " * 50, end="\r")
    console.print(f"[green]+ Satsuma Bot  - CREATED BY Alloidn[/green]", justify="center")
    console.print("-" * 50, style="green", justify="center")

# === CLI Menu ===
def display_menu():
    table = Table(title="[bold blue]Satsuma Bot Menu[/bold blue]", style="green", title_justify="center", show_header=False, expand=True)
    table.add_column(justify="center", style="cyan")
    
    options = [
        "1. Start Transactions",
        "2. Set Transaction Count",
        "3. Manual Swap",
        "4. Add Liquidity",
        "5. Convert SUMA to veSUMA",
        "6. Stake veSUMA",
        "7. Vote with veSUMA",
        "8. Exit"
    ]
    
    for opt in options:
        table.add_row(opt)
    
    console.print(table)
    choice = console.input("[bold magenta]> Select option (1-8): [/bold magenta]")
    return choice

# Load or initialize user settings
def load_user_settings():
    user_settings = {
        "transaction_count": 0,
        "current_round": 0
    }
    try:
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r') as f:
                data = json.load(f)
                user_settings["transaction_count"] = data.get("transaction_count", 0)
                console.print(f"[green]+ Loaded saved transaction count: {user_settings['transaction_count']}[/green]")
    except Exception as e:
        console.print(f"[red]- Error loading settings: {str(e)}[/red]")
    return user_settings

# Save transaction count to file
def save_transaction_count(count):
    try:
        with open(CONFIG_FILE, 'w') as f:
            json.dump({"transaction_count": count}, f)
        console.print(f"[green]+ Transaction count {count} saved successfully[/green]")
    except Exception as e:
        console.print(f"[red]- Error saving transaction count: {str(e)}[/red]")

# Generate random amount between 0.0001 and 0.0002
def generate_random_amount():
    min_amount = 0.0001
    max_amount = 0.0002
    random_amount = random.uniform(min_amount, max_amount)
    return round(random_amount, 6)

# Load configuration from .env
def load_config():
    display_banner()
    console.print("[yellow]> Loading configuration...[/yellow]", justify="center")
    
    config = {
        "rpc": "https://rpc.testnet.citrea.xyz",
        "chain_id": 5115,
        "symbol": "cBTC",
        "explorer": "https://explorer.testnet.citrea.xyz",
        "contract_address": Web3.to_checksum_address("0x3012e9049d05b4b5369d690114d5a5861ebb85cb"),
        "pool_address": Web3.to_checksum_address("0x080c376e6aB309fF1a861e1c3F91F27b8D4f1443"),
        "usdc_address": Web3.to_checksum_address("0x36c16eaC6B0Ba6c50f494914ff015fCa95B7835F"),
        "wcbtc_address": Web3.to_checksum_address("0x8d0c9d1c17ae5e40fff9be350f57840e9e66cd93"),
        "suma_address": Web3.to_checksum_address("0xdE4251dd68e1aD5865b14Dd527E54018767Af58a"),
        "vesuma_address": Web3.to_checksum_address("0x..."),  # Add actual veSUMA address
        "voting_contract": Web3.to_checksum_address("0x..."),  # Add actual voting contract address
        "staking_contract": Web3.to_checksum_address("0x..."),  # Add actual staking contract address
        "gauge_address": Web3.to_checksum_address("0x...")     # Add actual gauge address
    }

    return config

# Initialize Web3 provider
def initialize_provider(config):
    try:
        w3 = Web3(Web3.HTTPProvider(config["rpc"]))
        if not w3.is_connected():
            raise Exception("Failed to connect to RPC")
        console.print(f"[green]+ Connected to {config['rpc']} (Chain ID: {config['chain_id']})[/green]")
        return w3
    except Exception as e:
        console.print(f"[red]- Provider initialization error: {str(e)}[/red]")
        sys.exit(1)

# Load private keys from environment variables
def get_private_keys():
    private_keys = []
    key = os.getenv("PRIVATE_KEY_1")
    if not key:
        console.print("[red]- No private key found in .env file[/red]")
        sys.exit(1)
    try:
        account = Web3().eth.account.from_key(key)
        console.print(f"[green]+ Loaded 1 private key[/green]")
        private_keys.append(key)
    except Exception as e:
        console.print(f"[red]- Invalid private key: {str(e)}[/red]")
        sys.exit(1)
    return private_keys

# ERC20 ABI
ERC20_ABI = [
    {
        "constant": False,
        "inputs": [
            {"name": "spender", "type": "address"},
            {"name": "amount", "type": "uint256"}
        ],
        "name": "approve",
        "outputs": [{"name": "", "type": "bool"}],
        "type": "function"
    },
    {
        "constant": True,
        "inputs": [{"name": "owner", "type": "address"}],
        "name": "balanceOf",
        "outputs": [{"name": "", "type": "uint256"}],
        "type": "function"
    },
    {
        "constant": True,
        "inputs": [
            {"name": "owner", "type": "address"},
            {"name": "spender", "type": "address"}
        ],
        "name": "allowance",
        "outputs": [{"name": "", "type": "uint256"}],
        "type": "function"
    }
]

# Swap Router ABI
SWAP_ROUTER_ABI = [
    {
        "inputs": [
            {
                "components": [
                    {"name": "tokenIn", "type": "address"},
                    {"name": "tokenOut", "type": "address"},
                    {"name": "deployer", "type": "address"},
                    {"name": "recipient", "type": "address"},
                    {"name": "deadline", "type": "uint256"},
                    {"name": "amountIn", "type": "uint256"},
                    {"name": "amountOutMinimum", "type": "uint256"},
                    {"name": "limitSqrtPrice", "type": "uint160"}
                ],
                "name": "params",
                "type": "tuple"
            }
        ],
        "name": "exactInputSingle",
        "outputs": [{"name": "amountOut", "type": "uint256"}],
        "stateMutability": "payable",
        "type": "function"
    },
    {
        "inputs": [
            {"name": "tokenA", "type": "address"},
            {"name": "tokenB", "type": "address"},
            {"name": "deployer", "type": "address"},
            {"name": "recipient", "type": "address"},
            {"name": "amountADesired", "type": "uint256"},
            {"name": "amountBDesired", "type": "uint256"},
            {"name": "amountAMin", "type": "uint256"},
            {"name": "amountBMin", "type": "uint256"},
            {"name": "deadline", "type": "uint256"}
        ],
        "name": "addLiquidity",
        "outputs": [
            {"name": "amountA", "type": "uint256"},
            {"name": "amountB", "type": "uint256"},
            {"name": "liquidity", "type": "uint128"}
        ],
        "stateMutability": "nonpayable",
        "type": "function"
    }
]

# Algebra Pool ABI
ALGEBRA_POOL_ABI = [
    {
        "constant": True,
        "inputs": [],
        "name": "getReserves",
        "outputs": [
            {"name": "", "type": "uint128"},
            {"name": "", "type": "uint128"}
        ],
        "type": "function"
    },
    {
        "constant": True,
        "inputs": [],
        "name": "token0",
        "outputs": [{"name": "", "type": "address"}],
        "type": "function"
    },
    {
        "constant": True,
        "inputs": [],
        "name": "token1",
        "outputs": [{"name": "", "type": "address"}],
        "type": "function"
    },
    {
        "constant": True,
        "inputs": [],
        "name": "factory",
        "outputs": [{"name": "", "type": "address"}],
        "type": "function"
    }
]

# veSUMA ABI
VESUMA_ABI = [
    {
        "name": "create_lock",
        "inputs": [
            {"name": "_value", "type": "uint256"},
            {"name": "_unlock_time", "type": "uint256"}
        ],
        "outputs": [],
        "type": "function"
    },
    {
        "name": "increase_amount",
        "inputs": [
            {"name": "_value", "type": "uint256"}
        ],
        "outputs": [],
        "type": "function"
    },
    {
        "name": "increase_unlock_time",
        "inputs": [
            {"name": "_unlock_time", "type": "uint256"}
        ],
        "outputs": [],
        "type": "function"
    }
]

# Staking ABI
STAKING_ABI = [
    {
        "name": "stake",
        "inputs": [
            {"name": "_amount", "type": "uint256"}
        ],
        "outputs": [],
        "type": "function"
    },
    {
        "name": "withdraw",
        "inputs": [
            {"name": "_amount", "type": "uint256"}
        ],
        "outputs": [],
        "type": "function"
    }
]

# Voting ABI
VOTING_ABI = [
    {
        "name": "vote",
        "inputs": [
            {"name": "gauge_addr", "type": "address"},
            {"name": "weight", "type": "uint256"}
        ],
        "outputs": [],
        "type": "function"
    },
    {
        "name": "vote_for_many_gauge_weights",
        "inputs": [
            {"name": "_gauge_addr", "type": "address[]"},
            {"name": "_weights", "type": "uint256[]"}
        ],
        "outputs": [],
        "type": "function"
    }
]

async def approve_token(w3, config, account, token_address, amount):
    try:
        token_contract = w3.eth.contract(address=token_address, abi=ERC20_ABI)
        nonce = w3.eth.get_transaction_count(account.address)
        console.print(f"[green]+ Approving token {token_address} for {account.address} with nonce {nonce}[/green]")

        allowance = token_contract.functions.allowance(account.address, config["contract_address"]).call()
        if allowance >= amount:
            console.print("[green]+ Sufficient token allowance already exists[/green]")
            return {"success": True, "nonce": nonce}

        console.print("[yellow]> Sending token approval transaction...[/yellow]")
        approve_tx = token_contract.functions.approve(config["contract_address"], amount).build_transaction({
            "from": account.address,
            "gas": 100000,
            "nonce": nonce
        })

        signed_tx = w3.eth.account.sign_transaction(approve_tx, private_key=account.key)
        tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        console.print("[yellow]> Waiting for approval transaction confirmation...[/yellow]")
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

        if receipt["status"] == 1:
            console.print(f"[green]+ Token approval successful! Tx: {config['explorer']}/tx/{tx_hash.hex()}[/green]")
            return {"success": True, "nonce": nonce + 1}
        else:
            console.print("[red]- Token approval transaction failed[/red]")
            return {"success": False, "nonce": nonce}
    except Exception as e:
        console.print(f"[red]- Token approval error for {account.address}: {str(e)}[/red]")
        return {"success": False, "nonce": nonce}

async def check_pool_reserves(w3, config, token0, token1):
    try:
        pool_contract = w3.eth.contract(address=config["pool_address"], abi=ALGEBRA_POOL_ABI)
        reserves = pool_contract.functions.getReserves().call()
        console.print(f"[green]+ Pool reserves for {token0} -> {token1}: {reserves[0] / 10**6} {token0}, {reserves[1] / 10**18} {token1}[/green]")
        return reserves
    except Exception as e:
        console.print(f"[red]- Failed to fetch pool reserves: {str(e)}[/red]")
        return None

async def swap_usdc_to_suma(w3, config, private_key):
    try:
        account = w3.eth.account.from_key(private_key)
        console.print(f"[blue]=== Processing swap for address: {account.address} ===[/blue]")

        random_amount = generate_random_amount()
        console.print(f"[green]+ Random amount generated: {random_amount} USDC[/green]")

        usdc_contract = w3.eth.contract(address=config["usdc_address"], abi=ERC20_ABI)
        balance = usdc_contract.functions.balanceOf(account.address).call()
        console.print(f"[green]+ USDC balance: {balance / 10**6} USDC[/green]")

        amount_in = int(random_amount * 10**6)
        if balance < amount_in:
            console.print(f"[red]- Insufficient USDC balance. Need: {random_amount} USDC[/red]")
            return

        await check_pool_reserves(w3, config, "USDC", "WCBTC")
        await check_pool_reserves(w3, config, "WCBTC", "SUMA")

        approval_amount = amount_in * 2
        approval_result = await approve_token(w3, config, account, config["usdc_address"], approval_amount)
        if not approval_result["success"]:
            console.print("[red]- Skipping swap due to USDC approval failure[/red]")
            return

        swap_router = w3.eth.contract(address=config["contract_address"], abi=SWAP_ROUTER_ABI)
        deadline = int(time.time()) + 20 * 60

        params_usdc_wcbtc = (
            config["usdc_address"],
            config["wcbtc_address"],
            Web3.to_checksum_address("0x0000000000000000000000000000000000000000"),
            account.address,
            deadline,
            amount_in,
            0,
            0
        )

        console.print(f"[green]+ Swap parameters: tokenIn={params_usdc_wcbtc[0]}, tokenOut={params_usdc_wcbtc[1]}, amountIn={amount_in / 10**6}[/green]")

        try:
            console.print("[yellow]> Estimating gas for USDC -> WCBTC transaction...[/yellow]")
            gas_estimate = swap_router.functions.exactInputSingle(params_usdc_wcbtc).estimate_gas({
                "from": account.address,
                "value": 0
            })
            console.print(f"[green]+ Estimated gas: {gas_estimate}[/green]")
        except Exception as e:
            console.print(f"[red]- Gas estimation failed: {str(e)}[/red]")
            return

        console.print("[yellow]> Sending USDC -> WCBTC transaction...[/yellow]")
        usdc_wcbtc_tx = swap_router.functions.exactInputSingle(params_usdc_wcbtc).build_transaction({
            "from": account.address,
            "value": 0,
            "gas": 500000,
            "nonce": approval_result["nonce"]
        })

        signed_tx = w3.eth.account.sign_transaction(usdc_wcbtc_tx, private_key=account.key)
        tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        console.print("[yellow]> Waiting for USDC -> WCBTC transaction confirmation...[/yellow]")
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

        if receipt["status"] != 1:
            console.print("[red]- USDC -> WCBTC transaction failed[/red]")
            console.print(f"[cyan]Transaction receipt: {receipt}[/cyan]")
            return
        console.print(f"[green]+ USDC -> WCBTC swap successful! Tx: {config['explorer']}/tx/{tx_hash.hex()}[/green]")

        wcbtc_contract = w3.eth.contract(address=config["wcbtc_address"], abi=ERC20_ABI)
        wcbtc_balance = wcbtc_contract.functions.balanceOf(account.address).call()
        console.print(f"[green]+ WCBTC balance: {wcbtc_balance / 10**18} WCBTC[/green]")

        if wcbtc_balance == 0:
            console.print("[red]- No WCBTC received, skipping WCBTC -> SUMA swap[/red]")
            return

        wcbtc_approval_result = await approve_token(w3, config, account, config["wcbtc_address"], wcbtc_balance)
        if not wcbtc_approval_result["success"]:
            console.print("[red]- Skipping swap due to WCBTC approval failure[/red]")
            return

        params_wcbtc_suma = (
            config["wcbtc_address"],
            config["suma_address"],
            Web3.to_checksum_address("0x0000000000000000000000000000000000000000"),
            account.address,
            deadline,
            wcbtc_balance,
            0,
            0
        )

        try:
            console.print("[yellow]> Estimating gas for WCBTC -> SUMA transaction...[/yellow]")
            gas_estimate = swap_router.functions.exactInputSingle(params_wcbtc_suma).estimate_gas({
                "from": account.address,
                "value": 0
            })
            console.print(f"[green]+ Estimated gas: {gas_estimate}[/green]")
        except Exception as e:
            console.print(f"[red]- Gas estimation failed: {str(e)}[/red]")
            return

        console.print("[yellow]> Sending WCBTC -> SUMA transaction...[/yellow]")
        wcbtc_suma_tx = swap_router.functions.exactInputSingle(params_wcbtc_suma).build_transaction({
            "from": account.address,
            "value": 0,
            "gas": 500000,
            "nonce": wcbtc_approval_result["nonce"]
        })

        signed_tx = w3.eth.account.sign_transaction(wcbtc_suma_tx, private_key=account.key)
        tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        console.print("[yellow]> Waiting for WCBTC -> SUMA transaction confirmation...[/yellow]")
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

        if receipt["status"] == 1:
            console.print(f"[green]+ WCBTC -> SUMA swap successful! Tx: {config['explorer']}/tx/{tx_hash.hex()}[/green]")
        else:
            console.print("[red]- WCBTC -> SUMA transaction failed[/red]")
            console.print(f"[cyan]Transaction receipt: {receipt}[/cyan]")

    except Exception as e:
        console.print(f"[red]- Swap error: {str(e)}[/red]")

async def run_transactions(w3, config, private_keys, transaction_count):
    console.print(f"[blue]=== Starting transaction round ===[/blue]")
    console.print(f"[green]+ Performing {transaction_count} transactions with random amounts (0.0001-0.0002 USDC)[/green]")

    for i in range(transaction_count):
        console.print(f"[blue]=== Transaction {i + 1}/{transaction_count} ===[/blue]")
        for private_key in private_keys:
            await swap_usdc_to_suma(w3, config, private_key)
            await asyncio.sleep(2)

        if i < transaction_count - 1:
            console.print("[yellow]> Waiting 30 seconds before next transaction...[/yellow]")
            await asyncio.sleep(30)

    console.print(f"[green]+ Transaction round completed![/green]")

async def set_transaction_count():
    while True:
        try:
            count = int(console.input("[bold magenta]> Enter Number of Transactions: [/bold magenta]"))
            if count <= 0:
                console.print("[red]- Invalid number entered. Please enter a positive number.[/red]")
                continue
            save_transaction_count(count)
            return count
        except ValueError:
            console.print("[red]- Invalid input. Please enter a valid number.[/red]")
        except Exception as e:
            console.print(f"[red]- Error getting user input: {str(e)}[/red]")

async def manual_swap(w3, config, private_keys):
    while True:
        try:
            count = int(console.input("[bold magenta]> Enter Number of Swaps: [/bold magenta]"))
            if count <= 0:
                console.print("[red]- Invalid number entered. Please enter a positive number.[/red]")
                continue
            console.print(f"[blue]=== Starting Manual Swap ===[/blue]")
            await run_transactions(w3, config, private_keys, count)
            break
        except ValueError:
            console.print("[red]- Invalid input. Please enter a valid number.[/red]")
        except Exception as e:
            console.print(f"[red]- Error getting user input: {str(e)}[/red]")

async def add_liquidity(w3, config, private_key):
    try:
        account = w3.eth.account.from_key(private_key)
        console.print(f"\n[blue]=== Adding Liquidity for: {account.address} ===[/blue]")
        
        # Get pool contract
        pool_contract = w3.eth.contract(address=config["pool_address"], abi=ALGEBRA_POOL_ABI)
        
        # Get token addresses
        token0_address = pool_contract.functions.token0().call()
        token1_address = pool_contract.functions.token1().call()
        factory_address = pool_contract.functions.factory().call()
        
        # Get reserves
        reserves = await check_pool_reserves(w3, config, "USDC", "WCBTC")
        if not reserves:
            return
        
        # Determine which token is USDC and which is WCBTC
        usdc_decimals = 6
        wcbtc_decimals = 18
        usdc_contract = w3.eth.contract(address=config["usdc_address"], abi=ERC20_ABI)
        wcbtc_contract = w3.eth.contract(address=config["wcbtc_address"], abi=ERC20_ABI)
        
        # Get balances
        usdc_balance = usdc_contract.functions.balanceOf(account.address).call()
        wcbtc_balance = wcbtc_contract.functions.balanceOf(account.address).call()
        
        console.print(f"[green]+ USDC Balance: {usdc_balance / 10**usdc_decimals:.6f}[/green]")
        console.print(f"[green]+ WCBTC Balance: {wcbtc_balance / 10**wcbtc_decimals:.6f}[/green]")
        
        # Get user input for amounts
        try:
            usdc_amount = float(console.input("[bold magenta]> Enter USDC amount to add: [/bold magenta]"))
            wcbtc_amount = float(console.input("[bold magenta]> Enter WCBTC amount to add: [/bold magenta]"))
        except ValueError:
            console.print("[red]- Invalid input. Please enter numbers.[/red]")
            return
            
        usdc_amount_wei = int(usdc_amount * 10**usdc_decimals)
        wcbtc_amount_wei = int(wcbtc_amount * 10**wcbtc_decimals)
        
        # Check balances
        if usdc_balance < usdc_amount_wei:
            console.print(f"[red]- Insufficient USDC. Need: {usdc_amount}, Have: {usdc_balance / 10**usdc_decimals}[/red]")
            return
        if wcbtc_balance < wcbtc_amount_wei:
            console.print(f"[red]- Insufficient WCBTC. Need: {wcbtc_amount}, Have: {wcbtc_balance / 10**wcbtc_decimals}[/red]")
            return
        
        # Calculate optimal ratio based on pool reserves
        reserve_usdc = reserves[0] if token0_address == config["usdc_address"] else reserves[1]
        reserve_wcbtc = reserves[1] if token1_address == config["wcbtc_address"] else reserves[0]
        
        # Calculate the required ratio
        ratio = reserve_usdc / reserve_wcbtc if reserve_wcbtc > 0 else 0
        
        # Calculate the required WCBTC for the given USDC
        required_wcbtc = (usdc_amount_wei * reserve_wcbtc) / reserve_usdc if reserve_usdc > 0 else 0
        
        # Calculate slippage tolerance (1%)
        slippage_tolerance = 0.01
        
        # Calculate minimum amounts
        min_usdc = usdc_amount_wei * (1 - slippage_tolerance)
        min_wcbtc = wcbtc_amount_wei * (1 - slippage_tolerance)
        
        console.print(f"[green]+ Pool Ratio: 1 WCBTC = {ratio / 10**12:.6f} USDC")
        console.print(f"[green]+ Required WCBTC for {usdc_amount} USDC: {required_wcbtc / 10**wcbtc_decimals:.6f}")
        console.print(f"[green]+ Using minimums: USDC={min_usdc / 10**usdc_decimals:.6f}, WCBTC={min_wcbtc / 10**wcbtc_decimals:.6f}")
        
        # Approve tokens
        console.print("[yellow]> Approving tokens...[/yellow]")
        usdc_approval = await approve_token(w3, config, account, config["usdc_address"], usdc_amount_wei)
        wcbtc_approval = await approve_token(w3, config, account, config["wcbtc_address"], wcbtc_amount_wei)
        
        if not usdc_approval["success"] or not wcbtc_approval["success"]:
            console.print("[red]- Token approval failed. Aborting liquidity add.[/red]")
            return
            
        # Get router contract
        router_contract = w3.eth.contract(address=config["contract_address"], abi=SWAP_ROUTER_ABI)
        deadline = int(time.time()) + 20 * 60  # 20 minutes
        
        # Build add liquidity transaction with slippage protection
        add_liq_tx = router_contract.functions.addLiquidity(
            config["usdc_address"],
            config["wcbtc_address"],
            factory_address,
            account.address,
            usdc_amount_wei,
            wcbtc_amount_wei,
            int(min_usdc),  # amountAMin with slippage
            int(min_wcbtc),  # amountBMin with slippage
            deadline
        ).build_transaction({
            "from": account.address,
            "gas": 500000,
            "nonce": w3.eth.get_transaction_count(account.address),
        })
        
        # Sign and send transaction
        signed_tx = w3.eth.account.sign_transaction(add_liq_tx, private_key=account.key)
        tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        console.print("[yellow]> Adding liquidity...[/yellow]")
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        
        if receipt["status"] == 1:
            console.print(f"[green]+ Liquidity added successfully! Tx: {config['explorer']}/tx/{tx_hash.hex()}[/green]")
        else:
            console.print("[red]- Liquidity add transaction failed[/red]")
            # Try to get revert reason
            try:
                tx = w3.eth.get_transaction(tx_hash)
                result = w3.eth.call({
                    'to': tx['to'],
                    'from': tx['from'],
                    'value': tx['value'],
                    'data': tx['input'],
                    'gas': tx['gas'],
                    'gasPrice': tx['gasPrice'],
                    'nonce': tx['nonce']
                }, receipt['blockNumber'] - 1)
                console.print(f"[red]- Transaction reverted: {result.hex()}[/red]")
            except Exception as e:
                console.print(f"[red]- Error decoding revert reason: {str(e)}[/red]")
            
    except Exception as e:
        console.print(f"[red]- Error adding liquidity: {str(e)}[/red]")

async def convert_to_vesuma(w3, config, private_key):
    try:
        account = w3.eth.account.from_key(private_key)
        console.print(f"\n[blue]=== Converting SUMA to veSUMA for: {account.address} ===[/blue]")
        
        # Get SUMA contract
        suma_contract = w3.eth.contract(address=config["suma_address"], abi=ERC20_ABI)
        
        # Get SUMA balance
        suma_balance = suma_contract.functions.balanceOf(account.address).call()
        console.print(f"[green]+ SUMA Balance: {suma_balance / 10**18:.6f} SUMA[/green]")
        
        if suma_balance == 0:
            console.print("[red]- No SUMA balance to convert[/red]")
            return
            
        # Get lock duration
        try:
            weeks = int(console.input("[bold magenta]> Enter lock duration in weeks (1-208): [/bold magenta]"))
            if weeks < 1 or weeks > 208:
                console.print("[red]- Invalid lock duration. Must be between 1 and 208 weeks.[/red]")
                return
        except ValueError:
            console.print("[red]- Invalid input. Please enter a valid number.[/red]")
            return
            
        # Calculate unlock time (current time + weeks in seconds)
        unlock_time = int(time.time()) + (weeks * 7 * 86400)
        
        # Approve veSUMA contract to spend SUMA
        approval_result = await approve_token(w3, config, account, config["suma_address"], suma_balance)
        if not approval_result["success"]:
            console.print("[red]- SUMA approval failed. Aborting conversion.[/red]")
            return
            
        # Get veSUMA contract
        vesuma_contract = w3.eth.contract(address=config["vesuma_address"], abi=VESUMA_ABI)
        
        # Build create_lock transaction
        create_lock_tx = vesuma_contract.functions.create_lock(
            suma_balance,
            unlock_time
        ).build_transaction({
            "from": account.address,
            "gas": 500000,
            "nonce": w3.eth.get_transaction_count(account.address),
        })
        
        # Sign and send transaction
        signed_tx = w3.eth.account.sign_transaction(create_lock_tx, private_key=account.key)
        tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        console.print("[yellow]> Creating veSUMA lock...[/yellow]")
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        
        if receipt["status"] == 1:
            console.print(f"[green]+ SUMA locked successfully! Tx: {config['explorer']}/tx/{tx_hash.hex()}[/green]")
            console.print(f"[green]+ Lock duration: {weeks} weeks[/green]")
        else:
            console.print("[red]- Lock creation transaction failed[/red]")
            
    except Exception as e:
        console.print(f"[red]- Error converting SUMA to veSUMA: {str(e)}[/red]")

async def stake_vesuma(w3, config, private_key):
    try:
        account = w3.eth.account.from_key(private_key)
        console.print(f"\n[blue]=== Staking veSUMA for: {account.address} ===[/blue]")
        
        # Get veSUMA contract
        vesuma_contract = w3.eth.contract(address=config["vesuma_address"], abi=ERC20_ABI)
        
        # Get veSUMA balance
        vesuma_balance = vesuma_contract.functions.balanceOf(account.address).call()
        console.print(f"[green]+ veSUMA Balance: {vesuma_balance / 10**18:.6f} veSUMA[/green]")
        
        if vesuma_balance == 0:
            console.print("[red]- No veSUMA balance to stake[/red]")
            return
            
        # Get amount to stake
        try:
            amount = float(console.input(f"[bold magenta]> Enter amount to stake (max {vesuma_balance / 10**18:.6f}): [/bold magenta]"))
            amount_wei = int(amount * 10**18)
            if amount_wei > vesuma_balance:
                console.print("[red]- Amount exceeds veSUMA balance[/red]")
                return
        except ValueError:
            console.print("[red]- Invalid input. Please enter a valid number.[/red]")
            return
            
        # Approve staking contract to spend veSUMA
        approval_result = await approve_token(w3, config, account, config["vesuma_address"], amount_wei)
        if not approval_result["success"]:
            console.print("[red]- veSUMA approval failed. Aborting staking.[/red]")
            return
            
        # Get staking contract
        staking_contract = w3.eth.contract(address=config["staking_contract"], abi=STAKING_ABI)
        
        # Build stake transaction
        stake_tx = staking_contract.functions.stake(
            amount_wei
        ).build_transaction({
            "from": account.address,
            "gas": 500000,
            "nonce": w3.eth.get_transaction_count(account.address),
        })
        
        # Sign and send transaction
        signed_tx = w3.eth.account.sign_transaction(stake_tx, private_key=account.key)
        tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        console.print("[yellow]> Staking veSUMA...[/yellow]")
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        
        if receipt["status"] == 1:
            console.print(f"[green]+ veSUMA staked successfully! Tx: {config['explorer']}/tx/{tx_hash.hex()}[/green]")
            console.print(f"[green]+ Amount staked: {amount} veSUMA[/green]")
        else:
            console.print("[red]- Staking transaction failed[/red]")
            
    except Exception as e:
        console.print(f"[red]- Error staking veSUMA: {str(e)}[/red]")

async def vote_with_vesuma(w3, config, private_key):
    try:
        account = w3.eth.account.from_key(private_key)
        console.print(f"\n[blue]=== Voting with veSUMA for: {account.address} ===[/blue]")
        
        # Get veSUMA contract
        vesuma_contract = w3.eth.contract(address=config["vesuma_address"], abi=ERC20_ABI)
        
        # Get veSUMA balance
        vesuma_balance = vesuma_contract.functions.balanceOf(account.address).call()
        console.print(f"[green]+ veSUMA Balance: {vesuma_balance / 10**18:.6f} veSUMA[/green]")
        
        if vesuma_balance == 0:
            console.print("[red]- No veSUMA balance to vote with[/red]")
            return
            
        # Get voting power
        voting_power = vesuma_balance
        console.print(f"[green]+ Voting Power: {voting_power / 10**18:.6f}[/green]")
        
        # Get voting weight
        try:
            weight = int(console.input("[bold magenta]> Enter voting weight (0-100): [/bold magenta]"))
            if weight < 0 or weight > 100:
                console.print("[red]- Invalid weight. Must be between 0 and 100.[/red]")
                return
        except ValueError:
            console.print("[red]- Invalid input. Please enter a valid number.[/red]")
            return
            
        # Calculate weight in contract terms (0-10000 where 10000 = 100%)
        weight_scaled = int(weight * 100)
        
        # Get voting contract
        voting_contract = w3.eth.contract(address=config["voting_contract"], abi=VOTING_ABI)
        
        # Build vote transaction
        vote_tx = voting_contract.functions.vote(
            config["gauge_address"],
            weight_scaled
        ).build_transaction({
            "from": account.address,
            "gas": 500000,
            "nonce": w3.eth.get_transaction_count(account.address),
        })
        
        # Sign and send transaction
        signed_tx = w3.eth.account.sign_transaction(vote_tx, private_key=account.key)
        tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        console.print("[yellow]> Submitting vote...[/yellow]")
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        
        if receipt["status"] == 1:
            console.print(f"[green]+ Vote submitted successfully! Tx: {config['explorer']}/tx/{tx_hash.hex()}[/green]")
            console.print(f"[green]+ Voted for gauge: {config['gauge_address']} with weight: {weight}%[/green]")
        else:
            console.print("[red]- Voting transaction failed[/red]")
            
    except Exception as e:
        console.print(f"[red]- Error voting with veSUMA: {str(e)}[/red]")

async def main():
    try:
        config = load_config()
        w3 = initialize_provider(config)
        private_keys = get_private_keys()
        user_settings = load_user_settings()

        while True:
            choice = display_menu()
            try:
                option = int(choice)
                if option == 8:
                    console.print("[yellow]> Exiting Satsuma Auto Bot...[/yellow]")
                    sys.exit(0)
                elif option == 1:
                    if user_settings["transaction_count"] == 0:
                        console.print("[red]- Transaction count not set. Please set transaction count first.[/red]")
                        continue
                    console.print(f"[blue]=== Starting Swap Transactions ===[/blue]")
                    user_settings["current_round"] += 1
                    await run_transactions(w3, config, private_keys, user_settings["transaction_count"])
                    console.print("[yellow]> Waiting 5 minutes before next round...[/yellow]")
                    await asyncio.sleep(300)
                elif option == 2:
                    user_settings["transaction_count"] = await set_transaction_count()
                elif option == 3:
                    await manual_swap(w3, config, private_keys)
                elif option == 4:
                    for private_key in private_keys:
                        await add_liquidity(w3, config, private_key)
                elif option == 5:
                    for private_key in private_keys:
                        await convert_to_vesuma(w3, config, private_key)
                elif option == 6:
                    for private_key in private_keys:
                        await stake_vesuma(w3, config, private_key)
                elif option == 7:
                    for private_key in private_keys:
                        await vote_with_vesuma(w3, config, private_key)
                else:
                    console.print("[red]- Invalid option. Please select 1-8.[/red]")
            except ValueError:
                console.print("[red]- Invalid input. Please enter a number.[/red]")
            except Exception as e:
                console.print(f"[red]- Error in main loop: {str(e)}[/red]")
                console.print("[yellow]> Waiting 5 minutes before retry...[/yellow]")
                await asyncio.sleep(300)

    except Exception as e:
        console.print(f"[red]- Main execution error: {str(e)}[/red]")
        sys.exit(1)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        console.print("[yellow]> Program interrupted. Exiting...[/yellow]")
        sys.exit(0)
