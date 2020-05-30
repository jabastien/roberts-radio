from gpiozero import MCP3008

pot1 = MCP3008(channel=0)
pot2 = MCP3008(channel=1)

while True:
    pot1_value = pot1.value
    pot2_value = pot2.value

    print("Pot 1: " + str(pot1_value))
    print("Pot 2: " + str(pot2_value))
    
