from web3 import Web3
from dotenv import load_dotenv
import asyncio
import random
import time
import sys
import os
import json
from datetime import datetime, timedelta

# Load environment variables
load_dotenv()

# Configuration files
CONFIG_FILE = "satsuma_config.json"
MAIN_CONFIG_FILE = "config.json" 

# Terminal Colors
class Colors:
    RESET = '\033[0m'
    CYAN = '\033[36m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    RED = '\033[31m'
    WHITE = '\033[37m'
    BOLD = '\033[1m'
    PURPLE = '\033[35m'

class Logger:
    @staticmethod
    def info(msg):
        print(f"{Colors.GREEN}[✓] {msg}{Colors.RESET}")

    @staticmethod
    def warn(msg):
        print(f"{Colors.YELLOW}[!] {msg}{Colors.RESET}")

    @staticmethod
    def error(msg):
        print(f"{Colors.RED}[✗] {msg}{Colors.RESET}")

    @staticmethod
    def success(msg):
        print(f"{Colors.GREEN}[+] {msg}{Colors.RESET}")

    @staticmethod
    def processing(msg):
        print(f"{Colors.CYAN}[⟳] {msg}{Colors.RESET}")

    @staticmethod
    def step(msg):
        print(f"{Colors.WHITE}[➤] {msg}{Colors.RESET}")

    @staticmethod
    def banner():
        os.system('cls' if os.name == 'nt' else 'clear')
        print(f"{Colors.CYAN}{Colors.BOLD}")
        print("-" * 50)
        print(" Satsuma auto bot ")
        print(" powered by Zona Airdrop ")
        print(" Group @ZonaAirdr0p ")
        print("-" * 50)
        print(f"{Colors.RESET}\n")

log = Logger()

# Contract ABIs
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
    },
    {
        "constant": True,
        "inputs": [],
        "name": "decimals",
        "outputs": [{"name": "", "type": "uint8"}],
        "type": "function"
    },
    {
        "constant": True,
        "inputs": [],
        "name": "symbol",
        "outputs": [{"name": "", "type": "string"}],
        "type": "function"
    }
]

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
    }
]

LIQUIDITY_ROUTER_ABI = [
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
        "inputs": [{"name": "_value", "type": "uint256"}],
        "outputs": [],
        "type": "function"
    }
]

STAKING_ABI = [
    {
        "name": "stake",
        "inputs": [{"name": "_amount", "type": "uint256"}],
        "outputs": [],
        "type": "function"
    },
    {
        "name": "withdraw",
        "inputs": [{"name": "_amount", "type": "uint256"}],
        "outputs": [],
        "type": "function"
    }
]

VOTING_ABI = [
    {
        "name": "vote",
        "inputs": [
            {"name": "gauge_addr", "type": "address"},
            {"name": "weight", "type": "uint256"}
        ],
        "outputs": [],
        "type": "function"
    }
]

class SatsumaBot:
    def __init__(self):
        self.config = self.load_config()
        self.w3 = self.initialize_provider()
        self.private_keys = self.get_private_keys()
        self.settings = self.load_user_settings()
        self.transaction_history = []

    def load_config(self):
        config = {
            "rpc": "https://rpc.testnet.citrea.xyz",
            "chain_id": 5115,
            "symbol": "cBTC",
            "explorer": "https://explorer.testnet.citrea.xyz",
            "swap_router": Web3.to_checksum_address("0x3012e9049d05b4b5369d690114d5a5861ebb85cb"),
            "liquidity_router": Web3.to_checksum_address("0x55a4669cd6895EA25C174F13E1b49d69B4481704"),
            "pool_address": Web3.to_checksum_address("0x080c376e6aB309fF1a861e1c3F91F27b8D4f1443"),
            "usdc_address": Web3.to_checksum_address("0x36c16eaC6B0Ba6c50f494914ff015fCa95B7835F"),
            "wcbtc_address": Web3.to_checksum_address("0x8d0c9d1c17ae5e40fff9be350f57840e9e66cd93"),
            "suma_address": Web3.to_checksum_address("0xdE4251dd68e1aD5865b14Dd527E54018767Af58a"),
            "vesuma_address": Web3.to_checksum_address("0x0000000000000000000000000000000000000000"),
            "voting_contract": Web3.to_checksum_address("0x0000000000000000000000000000000000000000"),
            "staking_contract": Web3.to_checksum_address("0x0000000000000000000000000000000000000000"),
            "gauge_address": Web3.to_checksum_address("0x0000000000000000000000000000000000000000")
        }
        
        try:
            if os.path.exists(MAIN_CONFIG_FILE):
                with open(MAIN_CONFIG_FILE, 'r') as f:
                    loaded_config = json.load(f)
                    config.update(loaded_config)
                log.success(f"Konfigurasi dimuat dari {MAIN_CONFIG_FILE}")
            else:
                with open(MAIN_CONFIG_FILE, 'w') as f:
                    json.dump(config, f, indent=2)
                log.warn(f"File konfigurasi '{MAIN_CONFIG_FILE}' tidak ditemukan. Membuat file baru dengan konfigurasi default.")
        except json.JSONDecodeError:
            log.error(f"Error membaca '{MAIN_CONFIG_FILE}'. Pastikan format JSON benar.")
            sys.exit(1)
        except Exception as e:
            log.warn(f"Tidak dapat memuat atau menyimpan file konfigurasi: {str(e)}")
            
        return config

    def initialize_provider(self):
        try:
            w3 = Web3(Web3.HTTPProvider(self.config["rpc"]))
            if not w3.is_connected():
                raise Exception("Gagal terhubung ke RPC. Periksa koneksi internet atau URL RPC.")
            
            log.success(f"Terhubung ke {self.config['rpc']}")
            log.info(f"Chain ID: {self.config['chain_id']}")
            return w3
        except Exception as e:
            log.error(f"Inisialisasi provider gagal: {str(e)}")
            log.warn("Pastikan URL RPC Anda benar dan aktif.")
            sys.exit(1)

    def get_private_keys(self):
        private_keys = []
        key = os.getenv("PRIVATE_KEY_1")
        
        if not key or key == "your_private_key_here":
            log.error("Tidak ada private key yang valid ditemukan di environment variables (.env)")
            log.info("Silakan atur PRIVATE_KEY_1 di file .env Anda dengan private key asli Anda.")
            
            key = input("Masukkan private key Anda (tanpa awalan 0x, tekan Enter untuk keluar): ").strip()
            if not key:
                sys.exit(1)
        
        if key.startswith('0x'):
            key = key[2:]

        try:
            account = Web3().eth.account.from_key(key)
            log.success(f"Private key dimuat untuk alamat: {account.address}")
            private_keys.append(key)
        except Exception as e:
            log.error(f"Private key tidak valid: {str(e)}")
            sys.exit(1)
            
        return private_keys

    def load_user_settings(self):
        user_settings = {
            "transaction_count": 0,
            "current_round": 0,
            "total_transactions": 0,
            "successful_transactions": 0,
            "failed_transactions": 0,
            "last_transaction_time": None
        }
        
        try:
            if os.path.exists(CONFIG_FILE):
                with open(CONFIG_FILE, 'r') as f:
                    data = json.load(f)
                    user_settings.update(data)
                log.success(f"Konfigurasi pengguna dimuat dari '{CONFIG_FILE}'. Jumlah transaksi yang direncanakan: {user_settings['transaction_count']}")
            else:
                log.warn(f"File konfigurasi pengguna '{CONFIG_FILE}' tidak ditemukan. Menggunakan pengaturan default.")
        except json.JSONDecodeError:
            log.error(f"Error membaca '{CONFIG_FILE}'. Pastikan format JSON benar. Menggunakan pengaturan default.")
        except Exception as e:
            log.error(f"Gagal memuat pengaturan pengguna: {str(e)}. Menggunakan pengaturan default.")
            
        return user_settings

    def save_user_settings(self):
        try:
            with open(CONFIG_FILE, 'w') as f:
                json.dump(self.settings, f, indent=2)
            log.info("Konfigurasi pengguna berhasil disimpan.")
        except Exception as e:
            log.error(f"Gagal menyimpan pengaturan pengguna: {str(e)}")

    def generate_random_amount(self, min_amount=0.0001, max_amount=0.0002):
        random_amount = random.uniform(min_amount, max_amount)
        return round(random_amount, 6)

    async def approve_token(self, account, token_address, spender_address, amount):
        try:
            if not self.w3.is_checksum_address(token_address):
                log.error(f"Alamat token tidak valid: {token_address}")
                return {"success": False, "nonce": None}
            if not self.w3.is_checksum_address(spender_address):
                log.error(f"Alamat spender tidak valid: {spender_address}")
                return {"success": False, "nonce": None}

            token_contract = self.w3.eth.contract(address=token_address, abi=ERC20_ABI)
            nonce = self.w3.eth.get_transaction_count(account.address)
            
            log.processing(f"Memeriksa izin (allowance) untuk token {token_address} oleh spender {spender_address}...")
            
            allowance = token_contract.functions.allowance(account.address, spender_address).call()
            if allowance >= amount:
                log.success("Izin yang cukup sudah ada. Tidak perlu persetujuan.")
                return {"success": True, "nonce": nonce}
            
            log.processing(f"Mengirim transaksi persetujuan untuk {amount / (10**18):.6f} token...")
            
            approve_tx = token_contract.functions.approve(spender_address, amount).build_transaction({
                "from": account.address,
                "gas": 100000,
                "gasPrice": self.w3.eth.gas_price,
                "nonce": nonce,
                "chainId": self.config["chain_id"]
            })
            
            signed_tx = self.w3.eth.account.sign_transaction(approve_tx, private_key=account.key)
            tx_hash = self.w3.eth.send_raw_transaction(signed_tx.raw_transaction)
            
            log.processing(f"Menunggu konfirmasi persetujuan... Tx: {self.config['explorer']}/tx/{tx_hash.hex()}")
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=300)
            
            if receipt and receipt["status"] == 1:
                log.success(f"Persetujuan berhasil! Tx: {self.config['explorer']}/tx/{tx_hash.hex()}")
                return {"success": True, "nonce": nonce + 1}
            else:
                log.error(f"Transaksi persetujuan gagal. Receipt: {receipt}")
                return {"success": False, "nonce": nonce}
                
        except Exception as e:
            log.error(f"Error persetujuan: {str(e)}")
            return {"success": False, "nonce": nonce if 'nonce' in locals() else None}

    async def get_token_balance(self, token_address, account_address):
        try:
            if not self.w3.is_checksum_address(token_address):
                log.error(f"Alamat token tidak valid: {token_address}")
                return None
            if not self.w3.is_checksum_address(account_address):
                log.error(f"Alamat akun tidak valid: {account_address}")
                return None

            token_contract = self.w3.eth.contract(address=token_address, abi=ERC20_ABI)
            balance = token_contract.functions.balanceOf(account_address).call()
            decimals = token_contract.functions.decimals().call()
            symbol = token_contract.functions.symbol().call()
            
            return {
                "balance": balance,
                "decimals": decimals,
                "symbol": symbol,
                "formatted": balance / (10 ** decimals)
            }
        except Exception as e:
            log.error(f"Error mendapatkan saldo token untuk {token_address}: {str(e)}")
            return None

    async def perform_swap(self, private_key, token_in_address, token_out_address, amount_in_float):
        try:
            account = self.w3.eth.account.from_key(private_key)
            log.step(f"Memulai swap untuk alamat: {account.address}")
            
            token_in_info = await self.get_token_balance(token_in_address, account.address)
            if not token_in_info:
                return {"success": False, "error": f"Gagal mendapatkan info token input {token_in_address}"}
            
            amount_in_wei = int(amount_in_float * (10**token_in_info['decimals']))
            log.info(f"Swap {amount_in_float:.6f} {token_in_info['symbol']} ({amount_in_wei} wei) dari {token_in_address} ke {token_out_address}")

            if token_in_info['balance'] < amount_in_wei:
                log.error(f"Saldo {token_in_info['symbol']} tidak cukup untuk swap ini. Diperlukan: {amount_in_float:.6f}, Tersedia: {token_in_info['formatted']:.6f}")
                return {"success": False, "error": "Saldo token tidak cukup"}

            # --- Langkah Persetujuan (Approve) ---
            log.processing("Memulai proses persetujuan (approve) untuk token input...")
            approval_result = await self.approve_token(account, token_in_address, self.config["swap_router"], amount_in_wei)
            if not approval_result["success"]:
                return {"success": False, "error": "Persetujuan token gagal"}
            
            nonce = approval_result["nonce"]
            if nonce is None:
                nonce = self.w3.eth.get_transaction_count(account.address)

            # --- Persiapan Transaksi Swap ---
            swap_contract = self.w3.eth.contract(address=self.config["swap_router"], abi=SWAP_ROUTER_ABI)
            
            deadline = int(time.time()) + 300

            # Mengatur amountOutMinimum ke 99% dari amountIn (toleransi slippage 1%).
            # Ini lebih aman daripada 0, yang akan menerima slippage tak terbatas.
            amount_out_minimum = int(amount_in_wei * 0.99) 
            
            # --- PERBAIKAN PENTING ---
            # Mengatur limitSqrtPrice ke 1 (MIN_SQRT_RATIO) seperti pada transaksi yang berhasil Anda berikan.
            # Ini memungkinkan swap untuk melintasi semua tick ke arah harga yang relevan
            # tanpa terhenti oleh batasan harga tertentu di awal.
            limit_sqrt_price = 1 # Nilai yang terbukti berhasil dari TX Anda!
            
            log.info(f"Parameter Swap: amountIn={amount_in_float:.6f}, amountOutMinimum={amount_out_minimum}, limitSqrtPrice={limit_sqrt_price}")

            swap_params = {
                "tokenIn": token_in_address,
                "tokenOut": token_out_address,
                "deployer": account.address,
                "recipient": account.address,
                "deadline": deadline,
                "amountIn": amount_in_wei,
                "amountOutMinimum": amount_out_minimum, 
                "limitSqrtPrice": limit_sqrt_price 
            }
            
            gas_limit_estimate = 500000

            swap_tx = swap_contract.functions.exactInputSingle(swap_params).build_transaction({
                "from": account.address,
                "gas": gas_limit_estimate,
                "gasPrice": self.w3.eth.gas_price,
                "nonce": nonce,
                "chainId": self.config["chain_id"]
            })
            
            signed_tx = self.w3.eth.account.sign_transaction(swap_tx, private_key=private_key)
            tx_hash = self.w3.eth.send_raw_transaction(signed_tx.raw_transaction)
            
            log.processing(f"Menunggu konfirmasi swap... Tx: {self.config['explorer']}/tx/{tx_hash.hex()}")
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=300)
            
            if receipt and receipt["status"] == 1:
                log.success(f"Swap berhasil! Tx: {self.config['explorer']}/tx/{tx_hash.hex()}")
                self.transaction_history.append({
                    "type": "swap",
                    "tx_hash": tx_hash.hex(),
                    "timestamp": datetime.now().isoformat(),
                    "status": "success",
                    "account": account.address
                })
                return {"success": True, "tx_hash": tx_hash.hex()}
            else:
                log.error(f"Transaksi swap gagal. Receipt: {receipt}")
                log.error(f"Coba periksa di explorer untuk detail revert reason: {self.config['explorer']}/tx/{tx_hash.hex()}")
                return {"success": False, "error": "Transaksi gagal"}
                
        except Exception as e:
            log.error(f"Error swap: {str(e)}")
            return {"success": False, "error": str(e)}

    async def add_liquidity(self, private_key, token_a_address, token_b_address, amount_a_float, amount_b_float):
        try:
            account = self.w3.eth.account.from_key(private_key)
            log.step(f"Menambahkan likuiditas untuk alamat: {account.address}")
            
            token_a_info = await self.get_token_balance(token_a_address, account.address)
            token_b_info = await self.get_token_balance(token_b_address, account.address)

            if not token_a_info or not token_b_info:
                log.error("Gagal mendapatkan info token untuk menambahkan likuiditas.")
                return {"success": False, "error": "Gagal mendapatkan info token"}

            amount_a_wei = int(amount_a_float * (10**token_a_info['decimals']))
            amount_b_wei = int(amount_b_float * (10**token_b_info['decimals']))
            
            log.info(f"Menambahkan {amount_a_float:.6f} {token_a_info['symbol']} dan {amount_b_float:.6f} {token_b_info['symbol']}")

            if token_a_info['balance'] < amount_a_wei or token_b_info['balance'] < amount_b_wei:
                log.error("Saldo token tidak cukup untuk menambah likuiditas.")
                return {"success": False, "error": "Saldo token tidak cukup"}

            log.processing("Memulai persetujuan (approve) untuk Token A...")
            approval_a = await self.approve_token(account, token_a_address, self.config["liquidity_router"], amount_a_wei)
            if not approval_a["success"]:
                return {"success": False, "error": "Persetujuan Token A gagal"}
            
            log.processing("Memulai persetujuan (approve) untuk Token B...")
            approval_b = await self.approve_token(account, token_b_address, self.config["liquidity_router"], amount_b_wei)
            if not approval_b["success"]:
                return {"success": False, "error": "Persetujuan Token B gagal"}
            
            liquidity_contract = self.w3.eth.contract(address=self.config["liquidity_router"], abi=LIQUIDITY_ROUTER_ABI)
            
            deadline = int(time.time()) + 300
            nonce = self.w3.eth.get_transaction_count(account.address)
            
            amount_a_min = 0 
            amount_b_min = 0

            liquidity_tx = liquidity_contract.functions.addLiquidity(
                token_a_address, token_b_address, account.address, account.address,
                amount_a_wei, amount_b_wei, amount_a_min, amount_b_min, deadline
            ).build_transaction({
                "from": account.address,
                "gas": 400000,
                "gasPrice": self.w3.eth.gas_price,
                "nonce": nonce,
                "chainId": self.config["chain_id"]
            })
            
            signed_tx = self.w3.eth.account.sign_transaction(liquidity_tx, private_key=private_key)
            tx_hash = self.w3.eth.send_raw_transaction(signed_tx.raw_transaction)
            
            log.processing(f"Menunggu konfirmasi penambahan likuiditas... Tx: {self.config['explorer']}/tx/{tx_hash.hex()}")
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=300)
            
            if receipt and receipt["status"] == 1:
                log.success(f"Likuiditas berhasil ditambahkan! Tx: {self.config['explorer']}/tx/{tx_hash.hex()}")
                self.transaction_history.append({
                    "type": "liquidity",
                    "tx_hash": tx_hash.hex(),
                    "timestamp": datetime.now().isoformat(),
                    "status": "success",
                    "account": account.address
                })
                return {"success": True, "tx_hash": tx_hash.hex()}
            else:
                log.error(f"Transaksi penambahan likuiditas gagal. Receipt: {receipt}")
                return {"success": False, "error": "Transaksi gagal"}
                
        except Exception as e:
            log.error(f"Error penambahan likuiditas: {str(e)}")
            return {"success": False, "error": str(e)}

    async def convert_to_vesuma(self, private_key, amount_float, lock_time_days):
        try:
            account = self.w3.eth.account.from_key(private_key)
            log.step(f"Mengonversi SUMA ke veSUMA untuk alamat: {account.address}")
            
            if self.config["vesuma_address"] == Web3.to_checksum_address("0x0000000000000000000000000000000000000000"):
                log.error("Alamat kontrak veSUMA belum diatur. Silakan perbarui di config.json.")
                return {"success": False, "error": "Alamat veSUMA tidak valid"}

            suma_info = await self.get_token_balance(self.config["suma_address"], account.address)
            if not suma_info:
                log.error("Gagal mendapatkan info token SUMA.")
                return {"success": False, "error": "Gagal mendapatkan info token SUMA"}

            amount_wei = int(amount_float * (10**suma_info['decimals']))
            unlock_time = int(time.time()) + (lock_time_days * 24 * 60 * 60)
            
            log.info(f"Mengunci {amount_float:.6f} SUMA untuk {lock_time_days} hari.")

            if suma_info['balance'] < amount_wei:
                log.error(f"Saldo SUMA tidak cukup. Diperlukan: {amount_float:.6f}, Tersedia: {suma_info['formatted']:.6f}")
                return {"success": False, "error": "Saldo SUMA tidak cukup"}

            log.processing("Memulai persetujuan (approve) untuk token SUMA...")
            approval_result = await self.approve_token(account, self.config["suma_address"], self.config["vesuma_address"], amount_wei)
            if not approval_result["success"]:
                return {"success": False, "error": "Persetujuan SUMA gagal"}
            
            vesuma_contract = self.w3.eth.contract(address=self.config["vesuma_address"], abi=VESUMA_ABI)
            
            nonce = self.w3.eth.get_transaction_count(account.address)
            
            lock_tx = vesuma_contract.functions.create_lock(amount_wei, unlock_time).build_transaction({
                "from": account.address,
                "gas": 200000,
                "gasPrice": self.w3.eth.gas_price,
                "nonce": nonce,
                "chainId": self.config["chain_id"]
            })
            
            signed_tx = self.w3.eth.account.sign_transaction(lock_tx, private_key=private_key)
            tx_hash = self.w3.eth.send_raw_transaction(signed_tx.raw_transaction)
            
            log.processing(f"Menunggu konfirmasi konversi veSUMA... Tx: {self.config['explorer']}/tx/{tx_hash.hex()}")
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=300)
            
            if receipt and receipt["status"] == 1:
                log.success(f"Konversi veSUMA berhasil! Tx: {self.config['explorer']}/tx/{tx_hash.hex()}")
                self.transaction_history.append({
                    "type": "vesuma_conversion",
                    "tx_hash": tx_hash.hex(),
                    "timestamp": datetime.now().isoformat(),
                    "status": "success",
                    "account": account.address
                })
                return {"success": True, "tx_hash": tx_hash.hex()}
            else:
                log.error(f"Konversi veSUMA gagal. Receipt: {receipt}")
                return {"success": False, "error": "Transaksi gagal"}
                
        except Exception as e:
            log.error(f"Error konversi veSUMA: {str(e)}")
            return {"success": False, "error": str(e)}

    async def stake_vesuma(self, private_key, amount_float):
        try:
            account = self.w3.eth.account.from_key(private_key)
            log.step(f"Melakukan staking veSUMA untuk alamat: {account.address}")
            
            if self.config["staking_contract"] == Web3.to_checksum_address("0x0000000000000000000000000000000000000000"):
                log.error("Alamat kontrak Staking belum diatur. Silakan perbarui di config.json.")
                return {"success": False, "error": "Alamat staking tidak valid"}

            amount_wei = int(amount_float * 10**18) 
            
            log.info(f"Melakukan staking {amount_float:.6f} veSUMA.")

            staking_contract = self.w3.eth.contract(address=self.config["staking_contract"], abi=STAKING_ABI)
            
            nonce = self.w3.eth.get_transaction_count(account.address)
            
            stake_tx = staking_contract.functions.stake(amount_wei).build_transaction({
                "from": account.address,
                "gas": 200000,
                "gasPrice": self.w3.eth.gas_price,
                "nonce": nonce,
                "chainId": self.config["chain_id"]
            })
            
            signed_tx = self.w3.eth.account.sign_transaction(stake_tx, private_key=private_key)
            tx_hash = self.w3.eth.send_raw_transaction(signed_tx.raw_transaction)
            
            log.processing(f"Menunggu konfirmasi staking... Tx: {self.config['explorer']}/tx/{tx_hash.hex()}")
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=300)
            
            if receipt and receipt["status"] == 1:
                log.success(f"Staking veSUMA berhasil! Tx: {self.config['explorer']}/tx/{tx_hash.hex()}")
                self.transaction_history.append({
                    "type": "staking",
                    "tx_hash": tx_hash.hex(),
                    "timestamp": datetime.now().isoformat(),
                    "status": "success",
                    "account": account.address
                })
                return {"success": True, "tx_hash": tx_hash.hex()}
            else:
                log.error(f"Transaksi staking gagal. Receipt: {receipt}")
                return {"success": False, "error": "Transaksi gagal"}
                
        except Exception as e:
            log.error(f"Error staking veSUMA: {str(e)}")
            return {"success": False, "error": str(e)}

    async def vote_with_vesuma(self, private_key, gauge_address, weight):
        try:
            account = self.w3.eth.account.from_key(private_key)
            log.step(f"Melakukan voting dengan veSUMA untuk alamat: {account.address}")
            
            if self.config["voting_contract"] == Web3.to_checksum_address("0x0000000000000000000000000000000000000000"):
                log.error("Alamat kontrak Voting belum diatur. Silakan perbarui di config.json.")
                return {"success": False, "error": "Alamat voting tidak valid"}
            if not self.w3.is_checksum_address(gauge_address):
                log.error(f"Alamat gauge tidak valid: {gauge_address}")
                return {"success": False, "error": "Alamat gauge tidak valid"}

            log.info(f"Melakukan voting untuk gauge {gauge_address} dengan weight {weight}.")

            voting_contract = self.w3.eth.contract(address=self.config["voting_contract"], abi=VOTING_ABI)
            
            nonce = self.w3.eth.get_transaction_count(account.address)
            
            vote_tx = voting_contract.functions.vote(gauge_address, weight).build_transaction({
                "from": account.address,
                "gas": 200000,
                "gasPrice": self.w3.eth.gas_price,
                "nonce": nonce,
                "chainId": self.config["chain_id"]
            })
            
            signed_tx = self.w3.eth.account.sign_transaction(vote_tx, private_key=private_key)
            tx_hash = self.w3.eth.send_raw_transaction(signed_tx.raw_transaction)
            
            log.processing(f"Menunggu konfirmasi voting... Tx: {self.config['explorer']}/tx/{tx_hash.hex()}")
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=300)
            
            if receipt and receipt["status"] == 1:
                log.success(f"Voting berhasil! Tx: {self.config['explorer']}/tx/{tx_hash.hex()}")
                self.transaction_history.append({
                    "type": "voting",
                    "tx_hash": tx_hash.hex(),
                    "timestamp": datetime.now().isoformat(),
                    "status": "success",
                    "account": account.address
                })
                return {"success": True, "tx_hash": tx_hash.hex()}
            else:
                log.error(f"Transaksi voting gagal. Receipt: {receipt}")
                return {"success": False, "error": "Transaksi gagal"}
                
        except Exception as e:
            log.error(f"Error voting dengan veSUMA: {str(e)}")
            return {"success": False, "error": str(e)}

    async def start_automated_swaps(self):
        if self.settings["transaction_count"] <= 0:
            log.error("Jumlah transaksi belum diatur atau 0. Silakan atur jumlah transaksi terlebih dahulu.")
            return
        
        log.info(f"Memulai automated swaps dengan {self.settings['transaction_count']} transaksi.")
        
        tokens_for_swap = [self.config["usdc_address"], self.config["wcbtc_address"]]
        
        for i in range(self.settings["transaction_count"]):
            try:
                token_in = random.choice(tokens_for_swap)
                token_out = random.choice([t for t in tokens_for_swap if t != token_in])
                
                amount = self.generate_random_amount()
                
                private_key = random.choice(self.private_keys)
                
                log.step(f"Transaksi {i+1}/{self.settings['transaction_count']}")
                
                result = await self.perform_swap(private_key, token_in, token_out, amount)
                
                if result["success"]:
                    self.settings["successful_transactions"] += 1
                    log.success(f"Swap {i+1} selesai berhasil.")
                else:
                    self.settings["failed_transactions"] += 1
                    log.error(f"Swap {i+1} gagal: {result.get('error', 'Unknown error')}")
                    
                self.settings["total_transactions"] += 1
                self.settings["last_transaction_time"] = datetime.now().isoformat()
                
                self.save_user_settings()
                
                delay = random.uniform(5, 15)
                log.info(f"Menunggu {delay:.1f} detik sebelum transaksi berikutnya...")
                await asyncio.sleep(delay)
                
            except Exception as e:
                log.error(f"Error dalam transaksi {i+1}: {str(e)}")
                self.settings["failed_transactions"] += 1
                self.settings["total_transactions"] += 1
                self.save_user_settings()
                continue
        
        log.success("Automated swaps selesai!")
        log.info(f"Total: {self.settings['total_transactions']}, Berhasil: {self.settings['successful_transactions']}, Gagal: {self.settings['failed_transactions']}")

    def display_menu(self):
        print(f"\n{Colors.YELLOW}=== Menu Bot DeFi Satsuma ==={Colors.RESET}")
        print(f"{Colors.YELLOW}1. Mulai Automated Swaps{Colors.RESET}")
        print(f"{Colors.YELLOW}2. Atur Jumlah Transaksi{Colors.RESET}")
        print(f"{Colors.YELLOW}3. Swap Manual{Colors.RESET}")
        print(f"{Colors.YELLOW}4. Tambah Likuiditas{Colors.RESET}")
        print(f"{Colors.YELLOW}5. Konversi SUMA ke veSUMA{Colors.RESET}")
        print(f"{Colors.YELLOW}6. Staking veSUMA{Colors.RESET}")
        print(f"{Colors.YELLOW}7. Voting dengan veSUMA{Colors.RESET}")
        print(f"{Colors.YELLOW}8. Tampilkan Saldo{Colors.RESET}")
        print(f"{Colors.YELLOW}9. Riwayat Transaksi{Colors.RESET}")
        print(f"{Colors.YELLOW}10. Keluar{Colors.RESET}")
        print(f"{Colors.YELLOW}{'='*35}{Colors.RESET}")

    async def show_balances(self):
        try:
            account = self.w3.eth.account.from_key(self.private_keys[0])
            
            log.step(f"Menampilkan saldo untuk: {account.address}")
            
            eth_balance = self.w3.eth.get_balance(account.address)
            eth_formatted = self.w3.from_wei(eth_balance, 'ether')
            
            print(f"\n{Colors.CYAN}=== Saldo Akun ==={Colors.RESET}")
            print(f"{Colors.WHITE}Alamat: {account.address}{Colors.RESET}")
            print(f"{Colors.GREEN}Saldo {self.config['symbol']}: {eth_formatted:.6f} {self.config['symbol']}{Colors.RESET}")
            
            tokens = {
                "USDC": self.config["usdc_address"],
                "WCBTC": self.config["wcbtc_address"],
                "SUMA": self.config["suma_address"]
            }
            
            for symbol, address in tokens.items():
                balance_info = await self.get_token_balance(address, account.address)
                if balance_info:
                    print(f"{Colors.GREEN}Saldo {balance_info['symbol']}: {balance_info['formatted']:.6f} {balance_info['symbol']}{Colors.RESET}")
                else:
                    print(f"{Colors.RED}Saldo {symbol}: Error mengambil saldo{Colors.RESET}")
            
            if self.config["vesuma_address"] != Web3.to_checksum_address("0x0000000000000000000000000000000000000000"):
                vesuma_info = await self.get_token_balance(self.config["vesuma_address"], account.address)
                if vesuma_info:
                    print(f"{Colors.GREEN}Saldo {vesuma_info['symbol']}: {vesuma_info['formatted']:.6f} {vesuma_info['symbol']}{Colors.RESET}")
                else:
                    print(f"{Colors.RED}Saldo veSUMA: Error mengambil saldo (pastikan ABI dan alamat benar){Colors.RESET}")

            print(f"{Colors.CYAN}{'='*35}{Colors.RESET}")
            
        except Exception as e:
            log.error(f"Error menampilkan saldo: {str(e)}")

    def show_transaction_history(self):
        if not self.transaction_history:
            log.info("Tidak ada riwayat transaksi yang tersedia.")
            return
            
        print(f"\n{Colors.CYAN}=== Riwayat Transaksi ==={Colors.RESET}")
        
        for i, tx in enumerate(self.transaction_history[-10:], 1): 
            status_color = Colors.GREEN if tx["status"] == "success" else Colors.RED
            print(f"{Colors.WHITE}{i}. Tipe: {tx['type'].upper()}{Colors.RESET}")
            print(f"   Status: {status_color}{tx['status']}{Colors.RESET}")
            print(f"   Hash: {Colors.CYAN}{tx['tx_hash']}{Colors.RESET}")
            print(f"   Akun: {Colors.PURPLE}{tx.get('account', 'N/A')}{Colors.RESET}")
            print(f"   Waktu: {Colors.YELLOW}{tx['timestamp']}{Colors.RESET}")
            print("-" * 30)
            
        print(f"{Colors.CYAN}{'='*35}{Colors.RESET}")

    async def handle_menu_option(self, option):
        try:
            if option == "1":
                await self.start_automated_swaps()
                
            elif option == "2":
                try:
                    count_str = input("Masukkan jumlah transaksi yang diinginkan (angka > 0): ").strip()
                    if not count_str.isdigit():
                        log.error("Input tidak valid. Harap masukkan angka.")
                        return True
                    count = int(count_str)
                    
                    if count > 0:
                        self.settings["transaction_count"] = count
                        self.save_user_settings()
                        log.success(f"Jumlah transaksi diatur menjadi {count}.")
                    else:
                        log.error("Jumlah transaksi harus positif.")
                except ValueError:
                    log.error("Input jumlah transaksi tidak valid.")
                
            elif option == "3":
                print(f"\n{Colors.CYAN}=== Swap Manual ==={Colors.RESET}")
                print("Alamat token yang tersedia (dari config.json):")
                print(f"  USDC: {self.config['usdc_address']}")
                print(f"  WCBTC: {self.config['wcbtc_address']}")
                
                token_in_input = input("Masukkan alamat token input (misal USDC atau WCBTC): ").strip()
                token_out_input = input("Masukkan alamat token output (misal USDC atau WCBTC): ").strip()
                
                token_in_address = self.config['usdc_address'] if token_in_input.upper() == 'USDC' else \
                                  (self.config['wcbtc_address'] if token_in_input.upper() == 'WCBTC' else token_in_input)
                token_out_address = self.config['usdc_address'] if token_out_input.upper() == 'USDC' else \
                                   (self.config['wcbtc_address'] if token_out_input.upper() == 'WCBTC' else token_out_input)

                if not self.w3.is_checksum_address(token_in_address) or not self.w3.is_checksum_address(token_out_address):
                    log.error("Alamat token input atau output tidak valid. Harap masukkan alamat yang benar atau 'USDC'/'WCBTC'.")
                    return True

                try:
                    amount_str = input("Masukkan jumlah token input: ").strip()
                    if not amount_str.replace('.', '', 1).isdigit():
                        log.error("Input jumlah tidak valid. Harap masukkan angka.")
                        return True
                    amount = float(amount_str)
                    
                    if amount > 0:
                        result = await self.perform_swap(self.private_keys[0], Web3.to_checksum_address(token_in_address), Web3.to_checksum_address(token_out_address), amount)
                        if result["success"]:
                            log.success("Swap manual selesai berhasil.")
                        else:
                            log.error(f"Swap manual gagal: {result.get('error', 'Unknown error')}")
                    else:
                        log.error("Jumlah harus positif.")
                except ValueError:
                    log.error("Input jumlah tidak valid.")
                
            elif option == "4":
                print(f"\n{Colors.CYAN}=== Tambah Likuiditas ==={Colors.RESET}")
                print("Alamat token yang tersedia (dari config.json):")
                print(f"  USDC: {self.config['usdc_address']}")
                print(f"  WCBTC: {self.config['wcbtc_address']}")
                
                token_a_input = input("Masukkan alamat token A (misal USDC): ").strip()
                token_b_input = input("Masukkan alamat token B (misal WCBTC): ").strip()

                token_a_address = self.config['usdc_address'] if token_a_input.upper() == 'USDC' else \
                                 (self.config['wcbtc_address'] if token_a_input.upper() == 'WCBTC' else token_a_input)
                token_b_address = self.config['usdc_address'] if token_b_input.upper() == 'USDC' else \
                                 (self.config['wcbtc_address'] if token_b_input.upper() == 'WCBTC' else token_b_input)

                if not self.w3.is_checksum_address(token_a_address) or not self.w3.is_checksum_address(token_b_address):
                    log.error("Alamat token A atau B tidak valid. Harap masukkan alamat yang benar atau 'USDC'/'WCBTC'.")
                    return True

                try:
                    amount_a_str = input("Masukkan jumlah Token A: ").strip()
                    amount_b_str = input("Masukkan jumlah Token B: ").strip()

                    if not (amount_a_str.replace('.', '', 1).isdigit() and amount_b_str.replace('.', '', 1).isdigit()):
                        log.error("Input jumlah tidak valid. Harap masukkan angka.")
                        return True

                    amount_a = float(amount_a_str)
                    amount_b = float(amount_b_str)
                    
                    if amount_a > 0 and amount_b > 0:
                        result = await self.add_liquidity(self.private_keys[0], Web3.to_checksum_address(token_a_address), Web3.to_checksum_address(token_b_address), amount_a, amount_b)
                        if result["success"]:
                            log.success("Likuiditas berhasil ditambahkan.")
                        else:
                            log.error(f"Tambah likuiditas gagal: {result.get('error', 'Unknown error')}")
                    else:
                        log.error("Jumlah harus positif.")
                except ValueError:
                    log.error("Input jumlah tidak valid.")
                
            elif option == "5":
                print(f"\n{Colors.CYAN}=== Konversi SUMA ke veSUMA ==={Colors.RESET}")
                
                try:
                    amount_str = input("Masukkan jumlah SUMA: ").strip()
                    lock_days_str = input("Masukkan waktu kunci (hari): ").strip()

                    if not (amount_str.replace('.', '', 1).isdigit() and lock_days_str.isdigit()):
                        log.error("Input jumlah atau waktu kunci tidak valid. Harap masukkan angka.")
                        return True

                    amount = float(amount_str)
                    lock_days = int(lock_days_str)
                    
                    if amount > 0 and lock_days > 0:
                        result = await self.convert_to_vesuma(self.private_keys[0], amount, lock_days)
                        if result["success"]:
                            log.success("SUMA berhasil dikonversi ke veSUMA.")
                        else:
                            log.error(f"Konversi veSUMA gagal: {result.get('error', 'Unknown error')}")
                    else:
                        log.error("Jumlah dan waktu kunci harus positif.")
                except ValueError:
                    log.error("Input tidak valid.")
                
            elif option == "6":
                print(f"\n{Colors.CYAN}=== Staking veSUMA ==={Colors.RESET}")
                
                try:
                    amount_str = input("Masukkan jumlah veSUMA yang akan di-stake: ").strip()
                    if not amount_str.replace('.', '', 1).isdigit():
                        log.error("Input jumlah tidak valid. Harap masukkan angka.")
                        return True
                    amount = float(amount_str)
                    
                    if amount > 0:
                        result = await self.stake_vesuma(self.private_keys[0], amount)
                        if result["success"]:
                            log.success("veSUMA berhasil di-stake.")
                        else:
                            log.error(f"Staking veSUMA gagal: {result.get('error', 'Unknown error')}")
                    else:
                        log.error("Jumlah harus positif.")
                except ValueError:
                    log.error("Input jumlah tidak valid.")
                
            elif option == "7":
                print(f"\n{Colors.CYAN}=== Voting dengan veSUMA ==={Colors.RESET}")
                
                gauge_address_input = input("Masukkan alamat gauge: ").strip()
                if not self.w3.is_checksum_address(gauge_address_input):
                    log.error("Alamat gauge tidak valid.")
                    return True

                try:
                    weight_str = input("Masukkan weight vote (misal 100 untuk 100%): ").strip()
                    if not weight_str.isdigit():
                        log.error("Input weight tidak valid. Harap masukkan angka.")
                        return True
                    weight = int(weight_str)
                    
                    if weight > 0:
                        result = await self.vote_with_vesuma(self.private_keys[0], Web3.to_checksum_address(gauge_address_input), weight)
                        if result["success"]:
                            log.success("Voting berhasil.")
                        else:
                            log.error(f"Voting gagal: {result.get('error', 'Unknown error')}")
                    else:
                        log.error("Weight harus positif.")
                except ValueError:
                    log.error("Input weight tidak valid.")
                
            elif option == "8":
                await self.show_balances()
                
            elif option == "9":
                self.show_transaction_history()
                
            elif option == "10":
                log.info("Keluar dari Satsuma Bot...")
                return False
                
            else:
                log.error("Pilihan tidak valid. Silakan pilih 1-10.")
            
        except Exception as e:
            log.error(f"Error tak terduga saat menangani opsi menu: {str(e)}")
            
        return True

    async def run(self):
        log.banner()
        log.success("Satsuma DeFi Bot berhasil diinisialisasi!")
        
        if self.settings["total_transactions"] > 0:
            log.info(f"Status Terakhir: Total Transaksi: {self.settings['total_transactions']}, Berhasil: {self.settings['successful_transactions']}, Gagal: {self.settings['failed_transactions']}")
            if self.settings["last_transaction_time"]:
                last_time = datetime.fromisoformat(self.settings["last_transaction_time"])
                time_ago = datetime.now() - last_time
                log.info(f"Transaksi terakhir pada: {last_time.strftime('%Y-%m-%d %H:%M:%S')} ({str(time_ago).split('.')[0]} yang lalu)")
        
        while True:
            try:
                self.display_menu()
                choice = input(f"{Colors.WHITE}[➤] Pilih opsi (1-10): {Colors.RESET}").strip()
                
                if not choice:
                    continue
                
                should_continue = await self.handle_menu_option(choice)
                if not should_continue:
                    break
                
                await asyncio.sleep(1) 

            except KeyboardInterrupt:
                log.info("\nBot dihentikan oleh pengguna.")
                break
            except Exception as e:
                log.error(f"Error tak terduga di loop utama: {str(e)}")
                await asyncio.sleep(3)

async def main():
    bot = SatsumaBot()
    await bot.run()

if __name__ == "__main__":
    asyncio.run(main())
