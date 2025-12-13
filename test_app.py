import serial
import time
import sys
import os

# IMPORTAÇÃO DA SUA BIBLIOTECA (Assumindo a estrutura: projeto_raiz/victor86c_parser)
from victor86c_parser.parser import Victor86cParser
# A linha abaixo foi removida pois a função decode_victor_86c não existe mais:
# from victor86c_parser import decode_victor_86c 

# =================================================================
# 1. CONFIGURAÇÕES DA SERIAL
# =================================================================
PORTA_SERIAL = 'COM11'  # << AJUSTE A PORTA CONFORME SEU MULTÍMETRO
TAXA_BAUD = 2400
SERIAL_TIMEOUT = 0.5 
DADOS_LENGTH = 14       # Número de bytes de dados puros (sem CR/LF)

def monitorar_serial():
    """
    Conecta à porta serial, lê os dados brutos e os decodifica em tempo real
    usando a classe Victor86cParser.
    """
    try:
        ser = serial.Serial(PORTA_SERIAL, TAXA_BAUD, timeout=SERIAL_TIMEOUT)
        print(f"--- Conectado a {PORTA_SERIAL} | Taxa: {TAXA_BAUD} ---")
    except serial.SerialException as e:
        print(f"\nERRO: Falha ao abrir a porta serial {PORTA_SERIAL}: {e}")
        print("Verifique se a porta está correta e se o multímetro está ligado.")
        return

    print("Monitorando dados em tempo real. Pressione CTRL+C para sair.\n")
    
    # Variáveis para cálculo do intervalo
    last_measurement_time = None

    try:
        while True:
            # Tenta ler a linha completa (Dados + \r\n)
            linha_bytes = ser.readline()
            
            if linha_bytes:
                current_time_ms = int(time.time() * 1000)
                
                # Extrai apenas os 14 bytes de dados brutos
                pacote_dados = linha_bytes[:DADOS_LENGTH] 
                
                # Verifica se temos um pacote completo
                if len(pacote_dados) == DADOS_LENGTH:
                    
                    # 1. Calcular o intervalo de tempo
                    intervalo_ms = 0
                    if last_measurement_time is not None:
                        intervalo_ms = current_time_ms - last_measurement_time
                        
                    last_measurement_time = current_time_ms
                    
                    # 2. DECODIFICAÇÃO (USANDO A BIBLIOTECA)
                    # Cria a instância da classe com o pacote de dados
                    parser = Victor86cParser(pacote_dados)
                    
                    #print(f"Pacote Dados (14b): {parser.for_debug(0,14)}")
                    #print(f"Pacote Dados (14b): {parser.for_debug(10,11)}")
                    
                    # 3. Extrair os dados usando os métodos da classe
                    valor_final = parser.get_measurement_value()
                    unidade_completa = parser.get_unit_string()
                    modo_operacao = parser.get_mode()
                    
                    # 4. LOG NO CONSOLE
                    print(f"[{time.strftime('%H:%M:%S', time.localtime(current_time_ms/1000.0))}.{current_time_ms % 1000:03d}] "
                          f"VALOR: {valor_final:.3f} {unidade_completa} | "
                          f"MODO: {modo_operacao} | "
                          f"INT: {intervalo_ms} ms")
                
                elif len(linha_bytes) > 0:
                    # Log de pacotes incompletos ou lixo
                    print(f"Aviso: Pacote incompleto ou inválido ({len(linha_bytes)} bytes). Descartado.")

    except KeyboardInterrupt:
        print("\nMonitoramento interrompido pelo usuário.")

    except Exception as e:
        print(f"Ocorreu um erro inesperado: {e}")

    finally:
        if 'ser' in locals() and ser.is_open:
            ser.close()
            print("Porta serial fechada.")

if __name__ == "__main__":
    monitorar_serial()