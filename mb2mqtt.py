from pyModbusTCP.client import ModbusClient
import paho.mqtt.client as mqtt
from time import sleep
from threading import Thread
import sys


class ClienteMODBUS():
    """
    Classe Cliente MODBUS 
    """
    def __init__(self,server_addr,porta,device_id,broker_addr,broker_port,scan_time=0.2):
        """
        Construtor
        """
        self._scan_time = scan_time
        self._server_ip = server_addr
        self._device_id = device_id
        self._port = porta
        self._cliente = ModbusClient(host=server_addr, port=porta, unit_id=device_id)

        self._broker_addrs = broker_addr
        self._broker_port = broker_port
        self._client_mqtt = mqtt.Client()
        self._status_conn_mqtt = False

        self._threadread = None
        self._readingthread = False

    def atendimento(self):
        """
        Método para atendimento do usuário
        """
        try:
            print('\n--> Testing Modbus Connection.. ', end='')
            self._cliente.open()
            print('OK')
            print('--> Testing MQTT BROKER Connection.. ', end='')
            sleep(1)
            try:
                if self._client_mqtt.connect(self._broker_addrs, self._broker_port, 60) != 0:
                    print("Unable to establish connection with MQTT Broker!")
                    sys.exit(-1)
                else:
                    print('--> OK')
                    self._status_conn_mqtt = True
            except Exception as e:
                print('ERROR: ', e.args)
                print("\nUnable to establish connection with MQTT Broker!\nCheck if the IPv4 Address is OK and try again...")
                print('Following without connection with MQTT Broker..')
            self._client_mqtt.disconnect()
        except Exception as e:
            print('ERRO: ', e.args)

        try:
            atendimento = True
            while atendimento:
                print('-' * 100)
                print('ModbusTCP/MQTT Client'.center(100))
                print('-' * 100)
                sel = input("Available services: \n1- Start a read \n2- Stop a read \n3- Write a value \n4- Configuration \n5- Exit \nService N°: ")
                if sel == '1':
                    print('\nAvailable Function Codes:')
                    print("1- Coil Status \n2- Input Status \n3- Holding Register \n4- Input Register")
                    while True:
                        tipo = int(input("Function Code: "))
                        if tipo > 5:
                            print('Enter a valid type..')
                            sleep(0.5)
                        else:
                            break

                    if tipo == 3 or tipo == 4: 
                        while True:
                            #val = int(input("\nAvailable types of display:\n1- Decimal \n2- Floating Point \n3- Float Swapped \nDisplay: "))
                            val = 1
                            if val > 3:
                                print('Enter a valid type..')
                                sleep(0.5)
                            else:
                                break
                        if tipo == 3:
                            func = "F03-HoldingRegister"
                        else:
                            func = "F04-InputRegister"
                        if val == 1: #valores decimais
                            addr = int(input(f'\nModbus Starting Address: '))
                            leng = int(input(f'Quantity of Registers: '))
                            print('\nReading has started and data is being published to the specified topic...\n')
                            sleep(0.5)
                            try:
                                self._readingthread = True
                                self._threadread = Thread(target=self.readThread, args=(tipo, 1, addr, leng, func,))
                                self._threadread.start()
                            except Exception as e:
                                print('ERRO: ', e.args)
                                try:
                                    sleep(0.5)
                                    print('\nTentando novamente..')
                                    if not self._cliente.is_open():
                                        self._cliente.open()
                                    sleep(0.5)
                                    for i in range(0, int(nvezes)):
                                        print(f'Read {i + 1}:', end='')
                                        modbusValues = self.lerDado(int(tipo),int(addr),leng)
                                        print(modbusValues)
                                        self.mqttPublish(topic="test/status", msg=f"Leitura {i+1} {func}: {modbusValues}")
                                        sleep(self._scan_time)
                                    print('\nModbus reads have been published to broker via topic "test/status" successfully!!\n')
                                    sleep(0.5)
                                except Exception as e:
                                    print('ERRO: ', e.args)
                                    print('\nClient was unable to receive a response.. \nBack to menu..\n\n')
                                    sleep(1.5)

                        elif val == 2: #valores FLOAT
                            addr = int(input(f'\nModbus Starting Address: '))
                            leng = int(input(f'Quantity of Registers: '))
                            print('\nReading has started and data is being published to the specified topic...\n')
                            sleep(0.5)
                            try:
                                self._readingthread = True
                                self._threadread = Thread(target=self.readThread, args=(tipo, 2, addr, leng, func,))
                                self._threadread.start()
                            except Exception as e:
                                print('ERRO: ', e.args)
                                try:
                                    sleep(0.5)
                                    print('\nTentando novamente..')
                                    if not self._cliente.is_open():
                                        self._cliente.open()
                                    sleep(0.5)
                                    for i in range(0, int(nvezes)):
                                        print(f'Leitura {i + 1}:', end='')
                                        modbusValues = self.lerDadoFloat(int(tipo),int(addr),leng)
                                        print(modbusValues)
                                        self.mqttPublish(topic="test/status", msg=f"Leitura {i+1} {func}: {modbusValues}")
                                        sleep(self._scan_time)
                                    print('\nLeituras Modbus foram publicadas no broker através do tópico /test/status/ \nE inseridas no Banco de Dados local com sucesso!!\n')
                                    sleep(0.5)
                                except Exception as e:
                                    print('ERRO: ', e.args)
                                    print('\nO Cliente não conseguiu receber uma resposta.. \nVoltando ao menu..\n\n')
                                    sleep(1.5)

                        elif val == 3: #valores FLOAT SWAPPED 
                            addr = int(input(f'\nModbus Starting Address: '))
                            leng = int(input(f'Quantity of Registers: '))
                            nvezes = input('Quantidade de leituras: ')
                            print('\nReading has started and data is being published to the specified topic...\n')
                            sleep(0.5)
                            try:
                                for i in range(0, int(nvezes)):
                                    print(f'Leitura {i + 1}:', end='')
                                    modbusValues = self.lerDadoFloatSwapped(int(tipo), int(addr), leng)
                                    print(modbusValues)
                                    self.mqttPublish(topic="test/status", msg=f"Leitura {i+1} {func}: {modbusValues}")
                                    sleep(self._scan_time)
                                print('\nLeituras Modbus foram publicadas no broker através do tópico /test/status/ \nE inseridas no Banco de Dados local com sucesso!!\n')
                                sleep(0.5)
                            except Exception as e:
                                print('ERRO: ', e.args, '\n')
                                print('O Cliente não conseguiu receber uma resposta.. \nVoltando ao menu..\n\n')
                                sleep(1.5)

                        else:
                            print('Not found..\n')
                            sleep(0.7)

                    else:
                        addr = int(input(f'\nModbus Starting Address: '))
                        leng = int(input(f'Quantity of Registers: '))
                        nvezes = input('Quantidade de leituras: ')
                        print('\nReading has started and data is being published to the specified topic...\n')
                        sleep(0.3)
                        if tipo == 1:
                            func = "F01-CoilStatus"
                        else:
                            func = "F02-InputStatus"
                        try:
                            for i in range(0, int(nvezes)):
                                print(f'Leitura {i + 1}:', end='')
                                modbusValues = self.lerDado(int(tipo),int(addr),leng)
                                print(modbusValues)
                                self.mqttPublish(topic="test/status", msg=f"Leitura {i+1} {func}: {modbusValues}")
                                sleep(self._scan_time)
                            print('\nLeituras Modbus foram publicadas no broker através do tópico /test/status/ \nE inseridas no Banco de Dados local com sucesso!!\n')
                            sleep(0.5)
                        except Exception as e:
                            print('ERRO: ', e.args, '\n')
                            print('O Cliente não conseguiu receber uma resposta.. \nVoltando ao menu..\n\n')
                            sleep(1.5)

                elif sel == '2':
                    try:
                        self._readingthread = False
                        print("\nStopping reading..\n")
                    except Exception as e:
                        print('ERRO: ', e.args)
                        print('\nO Cliente não conseguiu escrever.. \nVoltando ao menu..\n\n')
                        sleep(1.5)

                elif sel == '3':
                    print('\nQual tipo de dado deseja escrever? \n1- Coil Status \n2- Holding Register')
                    while True:
                        tipo = int(input("Tipo: "))
                        if tipo > 2:
                            print('Digite um tipo válido..')
                            sleep(0.5)
                        else:
                            break
                    addr = input(f'Digite o endereço: ')
                    valor = int(input(f'Digite o valor que deseja escrever: '))
                    try:
                        print('\nEscrevendo..')
                        sleep(0.5)
                        self.escreveDado(int(tipo), int(addr), valor)
                    except Exception as e:
                        print('ERRO: ', e.args)
                        print('\nO Cliente não conseguiu escrever.. \nVoltando ao menu..\n\n')
                        sleep(1.5)

                elif sel == '4':
                    print('\nSettings: ')
                    print('1- Modbus Connection Settings \n2- MQTT Broker Settings \n3- Exit')
                    while True:
                        tpconfig = input("Set up: ")
                        if tpconfig not in '123':
                            print('Digite um tipo de configuração válido.. (1, 2 ou 3)')
                            sleep(0.5)
                        else:
                            break
                    if int(tpconfig) == 1:
                        print('')
                        print('-' * 100)
                        print('Modbus Communication Settings'.center(100))
                        print(f'\n-> Current settings: - IP Addrs: {self._server_ip} - TCP Port: {self._port} - Device ID: {self._device_id} - Scan_Time: {self._scan_time}s')
                        print('\nSettings: \n1- IP Address \n2- TCP Port  \n3- Device ID \n4- Scan Time \n5- Exit')
                        while True:
                            config = input("Set up: ")
                            if config not in '12345':
                                print('Digite um tipo de configuração válido.. (1, 2, 3, 4 ou 5)')
                                sleep(0.5)
                            else:
                                break
                        if int(config) == 1:
                            ipserv = str(input(' Novo endereço IP: '))
                            try:
                                self._cliente.close()
                                self._server_ip = ipserv
                                self._cliente = ModbusClient(host=self._server_ip)
                                self._cliente.open()
                                print(f'\nServer IP alterado para {ipserv} com sucesso!!\n')
                                sleep(0.5)
                            except Exception as e:
                                print('ERRO: ', e.args)
                                print('\nNão foi possível alterar o endereço IP.. \nVoltando ao menu..\n\n')
                                sleep(0.5)
                        elif int(config) == 2:
                            porttcp = input(' Nova porta TCP: ')
                            try:
                                self._cliente.close()
                                self._port = int(porttcp)
                                self._cliente = ModbusClient(port=self._port)
                                self._cliente.open()
                                print(f'\nTCP port alterado para {porttcp} com sucesso!!\n')
                                sleep(0.5)
                            except Exception as e:
                                print('ERRO: ', e.args)
                                print('\nNão foi possível alterar a porta.. \nVoltando ao menu..\n\n')
                                sleep(0.5)
                        elif int(config) == 3:
                            while True:
                                iddevice = input(' Novo device ID: ')
                                if 0 <= int(iddevice) < 256:
                                    break
                                else:
                                    print('Device ID deve ser um número inteiro entre 0 e 256.', end='')
                                    sleep(0.5)
                            try:
                                self._cliente.close()
                                self._device_id = int(iddevice)
                                self._cliente = ModbusClient(unit_id=self._device_id)
                                self._cliente.open()
                                print(f'\nDevice ID alterado para {iddevice} com sucesso!!\n')
                                sleep(0.5)
                            except Exception as e:
                                print('ERRO: ', e.args)
                                print('\nNão foi possível alterar o ID do device.. \nVoltando ao menu..\n\n')
                                sleep(0.5)
                        elif int(config) == 4:
                            scant = input(' Novo tempo de varredura [s]: ')
                            try:    
                                self._scan_time = float(scant)
                                print(f'\nScan_time alterado para {scant}s com sucesso!!\n')
                            except Exception as e:
                                print('ERRO: ', e.args)
                                print('\nNão foi possível alterar o tempo de varredura.. \nVoltando ao menu..\n\n')
                                sleep(0.5)
                        elif int(config) == 5:
                            print('\nGetting back...\n')
                            sleep(0.5)
                        else:
                            print('Not found..\n')
                            sleep(0.7)
                    elif int(tpconfig) == 2:
                        print('')
                        print('-' * 100)
                        print('MQTT Broker Settings'.center(100))
                        print(f'\n-> Current settings: - IP Addrs: {self._broker_addrs} - Port: {self._broker_port}')
                        print('\nSettings: \n1- IP Address \n2- Port \n3- Exit')
                        while True:
                            config = input("Set up: ")
                            if config not in '123':
                                print('Digite um tipo de configuração válido.. (1, 2 ou 3)')
                                sleep(0.5)
                            else:
                                break
                        if int(config) == 1:
                            ipserv = str(input(' Novo endereço IP do broker: '))
                            try:
                                self._broker_addrs = ipserv
                                print('\n--> Testando comunicação com o Broker MQTT.. ', end='')
                                sleep(0.5)
                                try:
                                    if self._client_mqtt.connect(self._broker_addrs, self._broker_port, 60) != 0:
                                        print("Não foi possível estabelecer conexão com o Broker MQTT!")
                                        sys.exit(-1)
                                    else:
                                        print(' --> Tudo OK')
                                        print(f'Broker IP alterado para {ipserv} com sucesso!!\n')
                                        self._status_conn_mqtt = True
                                        sleep(0.2)
                                except Exception as e:
                                    print('ERRO: ', e.args)
                                    print("\nNão foi possível estabelecer conexão com o Broker MQTT!\nVerifique se o Endereço IPv4 está OK e tente novamente..")
                                    print('Seguindo sem conexão com o Broker MQTT..')
                                    self._status_conn_mqtt = False
                                self._client_mqtt.disconnect()
                            except Exception as e:
                                print('ERRO: ', e.args)
                                print('\nNão foi possível alterar o endereço IP.. \nVoltando ao menu..\n\n')
                                sleep(0.5)
                        elif int(config) == 2:
                            portbroker = input(' Nova porta: ')
                            try:
                                self._broker_port = portbroker
                                print(f'\nPorta alterada para {portbroker} com sucesso!!\n')
                                sleep(0.5)
                            except Exception as e:
                                print('ERRO: ', e.args)
                                print('\nNão foi possível alterar a porta.. \nVoltando ao menu..\n\n')
                                sleep(0.5)
                        elif int(config) == 3:
                            print('\nGetting back...\n')
                            sleep(0.5)
                        else:
                            print('Not found..\n')
                            sleep(0.7)
                    else:
                        print('\nGetting back...\n')
                        sleep(0.5)
                elif sel == '5':
                    confirm_close = input('\nType "YES" to confirm you want to exit the app: ').capitalize()[0]
                    if confirm_close == 'Y':
                        sleep(0.2)
                        print('\nShutting down...\n')
                        sleep(1)
                        self._cliente.close()
                        atendimento = False
                    else:
                            print('\nGetting back..')
                else:
                    print('Not found..\n')
                    sleep(0.7)
        except Exception as e:
            print('ERRO: ', e.args)


    def lerDado(self, tipo, addr, leng=1):
        """
        Método para leitura MODBUS
        """
        if tipo == 1:
            co = self._cliente.read_coils(addr - 1, leng)
            tipo = "F01-CoilStatus"
            disp = "Decimal"
            return co

        elif tipo == 2:
            di = self._cliente.read_discrete_inputs(addr - 1, leng)
            tipo = "F02-InputStatus"
            disp = "Decimal"
            return di

        elif tipo == 3:
            hr = self._cliente.read_holding_registers(addr - 1, leng)
            tipo = "F03-HoldingRegister" 
            disp = "Decimal"
            return hr

        elif tipo == 4:
            ir = self._cliente.read_input_registers(addr - 1, leng)
            tipo = "F04-InputRegister" 
            disp = "Decimal"
            return ir

        else:
            print('Tipo de leitura inválido..')


    def lerDadoFloat(self, tipo, addr, leng):
        """
        Método para leitura FLOAT MODBUS
        """
        i = 0
        g = 0
        e1 = []
        listfloat = []
        while i < leng:
            if tipo == 3:
                i1 = self._cliente.read_holding_registers(addr - 1 + g, 2)
                tipore = "F03-HoldingRegister"
            elif tipo == 4:
                i1 = self._cliente.read_input_registers(addr - 1 + g, 2)
                tipore = "F04-InputRegister"
            else:
                print('Tipo inválido..')
            for x in i1:
                x = bin(x).lstrip("0b")
                e1.insert(0 + g, x)
            i += 1
            g += 2
        e = 0
        while e <= leng:
            e2 = ''
            for x in e1:
                e2 = str(f'{e2}{x.rjust(16, "0")} ')
            e += 1
        b2 = str(f'{e2}')
        e3 = b2.split()
        y = 0
        while y < len(e3):
            ieee = f'{e3[0+y]}{e3[1+y]}'
            sign = int(ieee[0])
            expo = str(ieee[1:9])
            expodec = 0
            expopot = 7
            for i in range(8):
                expodec = expodec + (int(expo[i]) * (2**expopot))
                expopot -= 1
            mant = str(ieee[9:])
            mantdec = 0
            mantpot = -1
            for i in range(23):
                mantdec = mantdec + (int(mant[i]) * (2 ** mantpot))
                mantpot -= 1
            value = ((-1)**sign)*(1+mantdec)*2**(expodec-127)
            listfloat.append(round(value, 3))
            y += 2
            tipo = tipore 
            disp = "Floating Point"
        return listfloat


    def lerDadoFloatSwapped(self, tipo, addr, leng):
        """
        Método para leitura FLOAT SWAPPED MODBUS
        """
        i = 0
        g = 0
        e1 = []
        listfloatsp = []
        while i < leng:
            if tipo == 3:
                i1 = self._cliente.read_holding_registers(addr - 1 + g, 2)
                tipore = "F03-HoldingRegister"
            elif tipo == 4:
                i1 = self._cliente.read_input_registers(addr - 1 + g, 2)
                tipore = "F04-InputRegister"
            else:
                print('Tipo inválido..')
            i2 = i1[::-1]
            for x in i2:
                x = bin(x).lstrip("0b")
                e1.insert(0 + g, x)
            i += 1
            g += 2
        e = 0
        while e <= leng:
            e2 = ''
            for x in e1:
                e2 = str(f'{e2}{x.rjust(16, "0")} ')
            e += 1
        b2 = str(f'{e2}')
        e3 = b2.split()
        y = 0
        while y < len(e3):
            ieee = f'{e3[0+y]}{e3[1+y]}'
            sign = int(ieee[0])
            expo = str(ieee[1:9])
            expodec = 0
            expopot = 7
            for i in range(8):
                expodec = expodec + (int(expo[i]) * (2**expopot))
                expopot -= 1
            mant = str(ieee[9:])
            mantdec = 0
            mantpot = -1
            for i in range(23):
                mantdec = mantdec + (int(mant[i]) * (2 ** mantpot))
                mantpot -= 1
            value = ((-1)**sign)*(1+mantdec)*2**(expodec-127)
            listfloatsp.append(round(value, 3))
            y += 2
            tipo = tipore
            disp = "Float (Swapped)"
        return listfloatsp


    def escreveDado(self, tipo, addr, valor):
        """
        Método para escrita MODBUS
        """
        try:
            if tipo == 1:
                print(f'Valor {valor} escrito no endereço {addr}\n')
                return self._cliente.write_single_coil(addr - 1, valor)
            elif tipo == 2:
                print(f'Valor {valor} escrito no endereço {addr}\n')
                return self._cliente.write_single_register(addr - 1, valor)
            else:
                print('Tipo de escrita inválido..\n')

        except Exception as e:
            print('ERRO: ', e.args)


    def mqttPublish(self, topic, msg):
        """
        Método para escrita MODBUS
        """
        try:
            if self._client_mqtt.connect(self._broker_addrs, self._broker_port, 60) != 0:
                print("Não foi possível estabelecer conexão com o Broker MQTT!")
                sys.exit(-1)
            self._client_mqtt.publish(topic, msg)
            sleep(0.2)
            self._client_mqtt.disconnect()
        except Exception as e:
            print('ERRO: ', e.args, end='')
            print('Erro ao tentar publicar no broker, confira o endereço IP e a porta do mesmo..')
            self._status_conn_mqtt = False

        
    def readThread(self, tipo, display, addr, leng, func):
        """
        Método para thread de leitura 1
        """
        if display == 1:
            try:
                i = 0
                while self._readingthread:
                    modbusValues = self.lerDado(int(tipo),int(addr),leng)
                    if self._status_conn_mqtt:
                        self.mqttPublish(topic="test/status", msg=f"Read {i+1} - ({addr}:{leng}) {func}: {modbusValues}")
                    sleep(self._scan_time)
                    i += 1
                    sleep(0.2)
            except Exception as e:
                print('ERRO: ', e.args, end='')
                print('Erro ao tentar publicar no broker, confira o endereço IP e a porta do mesmo..')

        elif display == 2:
            try:
                i = 0
                while self._readingthread:
                    modbusValues = self.lerDadoFloat(int(tipo),int(addr),leng)
                    if self._status_conn_mqtt:
                        self.mqttPublish(topic="test/status", msg=f"Read {i+1} - F03.HR (350-369): {modbusValues}")
                    sleep(self._scan_time)
                    i += 1
                    sleep(0.2)
            except Exception as e:
                print('ERRO: ', e.args, end='')
                print('Erro ao tentar publicar no broker, confira o endereço IP e a porta do mesmo..')

        elif display == 3:
            try:
                i = 0
                while self._readingthread:
                    modbusValues = self.lerDadoFloatSwapped(int(tipo),int(addr),leng)
                    if self._status_conn_mqtt:
                        self.mqttPublish(topic="test/status", msg=f"Read {i+1} - {func}: {modbusValues}")
                    sleep(self._scan_time)
                    i += 1
                    sleep(0.2)
            except Exception as e:
                print('ERRO: ', e.args, end='')
                print('Erro ao tentar publicar no broker, confira o endereço IP e a porta do mesmo..')