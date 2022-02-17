import pigpio

def main():
    
    pi = pigpio.pi()
    
    pi.set_mode(4, pigpio.OUTPUT)
    pi.write(4, 1)
    print(pi.read(4))
    
    pi.set_mode(27, pigpio.OUTPUT)
    pi.write(27, 1)
    print(pi.read(27))
    
    pi.set_mode(18, pigpio.OUTPUT)
    pi.write(18, 1)
    print(pi.read(18))
    
    pi.set_mode(23, pigpio.OUTPUT)
    pi.write(23, 1)
    print(pi.read(23))
    
    #pi.stop

if __name__ == "__main__":
    main()


