# PACOTE DE DADOS b'+3109 41\x00@\x80\x1f\r\n'

# Este arquivo contém a lógica de decodificação do protocolo VICTOR 86C
# Usa o novo mapeamento de bytes para retornar dados estruturados

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
            'is_beep': False,
            'is_diode': False,
            'unit': '',
            'mode': '',
            'is_auto': False,
            'is_rel': False,
            'is_hold': False,
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
        byte_mode = self._packet[7] 
        
        modes = []
        
        # Lógica Bitwise confirmada nos testes
        if byte_mode & 0x20: # Bit 5
            data['is_auto'] = True
            modes.append("AUTO")
            
        if byte_mode & 0x10: # Bit 4
            modes.append("DC")
            
        if byte_mode & 0x08: # Bit 3
            modes.append("AC")
            
        if byte_mode & 0x04: # Bit 2 (REL/Delta)
            data['is_rel'] = True
            modes.append("REL")
            
        if byte_mode & 0x02: # Bit 1
            data['is_hold'] = True
            modes.append("HOLD")
            
        # Junta tudo em uma string (ex: "AUTO AC REL")
        data['mode'] = " ".join(modes) if modes else "Unknown"
        
        # --- 5. MODO MAX/MIN (Bit 9 / Índice 8) ---
        byte_max_min = self._packet[8]
        data['max_min'] = '' # Valor padrão

        if byte_max_min & 0x20:   # Bit 5
            data['max_min'] = 'MAX'
        elif byte_max_min & 0x10: # Bit 4
            data['max_min'] = 'MIN'

        # --- 6. Símbolos/Prefixos (Bit 10 / Índice 9) ---
        byte_prefix = self._packet[9]
                
        # Unidades de Grandeza (Geralmente excludentes, usamos elif)
        if byte_prefix & 0x10:   # Bit 4
            data['prefix'] = 'M'
        elif byte_prefix & 0x01: # Bit 0
            data['prefix'] = ''
        elif byte_prefix & 0x40: # Bit 6
            data['prefix'] = 'm'
        elif byte_prefix & 0x80: # Bit 7
            data['prefix'] = 'u'
        elif byte_prefix & 0x20: # Bit 5
            data['prefix'] = 'k'
        elif byte_prefix == 0x00:
            data['prefix'] = ' '

        # Símbolos de Função (Podem ocorrer junto com prefixos?)
        if byte_prefix & 0x08: # Bit 3
            data['is_beep'] = True
            # O beep pode ser tratado como um modo ou símbolo separado
            
        if byte_prefix & 0x04: # Bit 2
            data['is_diode'] = True

        # --- 7. Unidade Base (Bit 11 / Índice 10) ---
        byte_unit = self._packet[10]
        data['unit'] = ''
        
        # Unidades são geralmente exclusivas, então usamos if/elif
        if byte_unit & 0x80:   # Bit 7
            data['unit'] = 'V'
        elif byte_unit & 0x40: # Bit 6
            data['unit'] = 'A'
        elif byte_unit & 0x20: # Bit 5
            data['unit'] = 'Ohms'
        elif byte_unit & 0x10: # Bit 4
            data['unit'] = 'hFE'
        elif byte_unit & 0x08: # Bit 3
            data['unit'] = 'Hz'
        elif byte_unit & 0x04: # Bit 2
            data['unit'] = 'F' # Farad
            if data['prefix'] == ' ':
                data['prefix'] = 'n' # Ajusta para nF se sem prefixo
        elif byte_unit & 0x02: # Bit 1
            data['unit'] = '°C'
        elif byte_unit & 0x01: # Bit 0
            data['unit'] = '°F'
        elif byte_unit == 0x00:
            data['unit'] = '%'

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