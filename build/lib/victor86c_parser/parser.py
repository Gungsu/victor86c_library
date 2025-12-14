# PACOTE DE DADOS b'+3109 41\x00@\x80\x1f\r\n'

# Este arquivo contém a lógica de decodificação do protocolo VICTOR 86C
# Usa o novo mapeamento de bytes para retornar dados estruturados

# Mapeamento do Byte 7 (Índice 7): Modos AC/DC/HOLD/AUTO
MODE_MAP = {
    b'1': 'DC',          # 1: DC
    b'\x11': 'DC',       # 11 hex: DC
    b'\x10': 'DC',       # 10 hex: DC
    b')': 'AC',          # ): AC
    b'\t': 'AC',
    b'\x08': 'AC',       
    b'!': 'AUTO',        # !: NADA (geralmente indica AUTO)
    b' ': 'AUTO',        # !: NADA (geralmente indica AUTO)
    b'#': 'AUTO HOLD',   # #: AUTO HOLD
    b'\x02': 'HOLD',     # 02 hex: HOLD
    b'3': 'HOLD',        # 3: HOLD
    b'\x0b': 'HOLD',     # HOLD AC DC (exemplo de combinação)
    b'\x13': 'HOLD',
    b'"': 'HOLD',
    b'\x00': '',         # Nenhum modo específico
    b'\x01': '',
}

# Mapeamento do Byte 9 (Índice 8): Indicador MAX/MIN
MAX_MIN_MAP = {
    b'\x20': 'MAX',
    b'\x10': 'MIN',
    b'\x00': '', # Nenhum
    b' ': 'MAX',
}

# Mapeamento do Byte 10 (Índice 9): Prefixos e Símbolos
PREFIX_MAP = {
    b'\x00': 'n',       # Nano (n)
    b'\x10': 'M',        # Mega (M)
    b'@': 'm',           # Mili (m)
    b'\x80': 'u',        # Micro (u)
    b'\x04': 'DIODE ',    # Símbolo de diodo (-->|)
    b'\x08': 'BEEP ',     # Símbolo de beep
    b'\x01': 'K',        # Kilo (K)
    b' ': '',            # Nenhum prefixo
}

# Mapeamento do Byte 11 (Índice 10): Unidades Base
UNIT_MAP = {
    b'2': 'C',
    b'1': 'F',
    b'@': 'A',
    b'\x80': 'V',
    b'\x04': 'F',
    b'\x08': 'Hz',
    b'\x02': 'ºC',
    b' ': 'Ohms',
}

class Victor86cParser:
    """
    Classe utilitária para decodificar e acessar dados de um pacote
    serial de 14 bytes do multímetro VICTOR 86C.
    """
    def __init__(self, pacote: bytes):
        """Inicializa o parser com o pacote de 14 bytes."""
        self._packet = pacote[:14]
        self._data = self._parse_data()
        
    def _parse_data(self):
        """Decodifica o pacote e retorna um dicionário de dados."""
        if len(self._packet) < 14:
            return {"error": "Pacote incompleto ou inválido."}

        # Inicializa campos
        data = {
            'value_raw': None,
            'decimal_position': 0,
            'prefix': '',
            'unit': '',
            'mode': '',
            'max_min': '',
            'bargraph': 0,
            'sign': 1, # 1 para positivo, -1 para negativo
            'raw_bytes': self._packet
        }

        # --- 1. Sinal (Byte 0 / Índice 0) ---
        if self._packet[0:1] == b'-':
            data['sign'] = -1
        
        # --- 2. Valor Numérico (Bytes 1-4 / Índices 1-4) ---
        try:
            valor_str_bytes = self._packet[1:5]
            if valor_str_bytes == b'?0:?':
                valor_string = "OL"
                data['value_raw'] = valor_string
            else:
                valor_string = valor_str_bytes.decode('utf-8', errors='ignore')
                data['value_raw'] = int(valor_string)
        except Exception:
            return {"error": f"Falha ao decodificar valor numérico: {self._packet[1:5]}"}

        # --- 3. Localização do Ponto Decimal (Bit 7 / Índice 6) ---
        try:
            valor_bit_7 = self._packet[6:7].decode('utf-8', errors='ignore')
            if valor_bit_7 == '1':
                data['decimal_position'] = 3 # /1000
            elif valor_bit_7 == '2':
                data['decimal_position'] = 2 # /100
            elif valor_bit_7 == '4':
                data['decimal_position'] = 1 # /10
        except:
            pass 

        # --- 4. Modo de Medição (Bit 8 / Índice 7) ---
        data['mode'] = MODE_MAP.get(self._packet[7:8], 'Unknown')
        
        # --- 5. MODO MAX/MIN (Bit 9 / Índice 8) ---
        data['max_min'] = MAX_MIN_MAP.get(self._packet[8:9], '')

        # --- 6. Símbolos/Prefixos (Bit 10 / Índice 9) ---
        data['prefix'] = PREFIX_MAP.get(self._packet[9:10], '')

        # --- 7. Unidade Base (Bit 11 / Índice 10) ---
        data['unit'] = UNIT_MAP.get(self._packet[10:11], 'Unknown')

        # --- 8. Barra Inferior (Bit 12 / Índice 11) ---
        try:
            data['bargraph'] = int.from_bytes(self._packet[11:12], byteorder='big')
        except:
             pass

        return data

    def get_measurement_value(self) -> float:
        """Calcula e retorna o valor final da medição como um float."""
        
        if "error" in self._data:
            return float('nan') # Not a Number em caso de erro

        raw_val = self._data['value_raw']
        sign = self._data['sign']
        
        if raw_val == "OL":
            return float('inf') # Representa Overload como infinito
        
        # Aplica a posição decimal
        if self._data['decimal_position'] > 0:
            value = raw_val / (10 ** self._data['decimal_position'])
        else:
            value = raw_val

        return sign * value

    def get_unit_string(self) -> str:
        """Retorna a unidade completa (ex: mV, kOhms, uA)."""
        if "error" in self._data:
            return "ERR"
        
        # Combina prefixo + unidade base
        return self._data['prefix'] + self._data['unit']

    def get_mode(self) -> str:
        """Retorna o modo de medição (ex: AC, DC, HOLD)."""
        return self._data.get('mode', 'Unknown')
    
    def get_bargraph_value(self) -> int:
        """Retorna o valor da barra inferior (bargraph)."""
        return self._data.get('bargraph', 0)
    
    def get_max_min_mode(self) -> str:
        """Retorna o modo MAX/MIN ativo."""
        return self._data.get('max_min', '')
    
    def get_raw_slice(self, start: int, end: int) -> bytes:
        """
        Retorna uma fatia (slice) dos bytes brutos do pacote para depuração.
        Ex: get_raw_slice(8, 9) para ver o byte do MAX/MIN.
        """
        return self._packet[start:end]