def main():
    while True:
        cost = input("Please enter the price of the product: ")
        print("Price of product: "+ cost)
        cashReceived = input("Please enter the cash received: ")
        print("Amount of cash given: " + cashReceived)
        
        change = int(cashReceived) - int(cost)
      
        denominations = [1000, 100, 50, 10, 5, 2, 1]
        sum = 0
        print("Denominations to return: ")
        for i in denominations:
            if change < 0:
                print("Cash given is less than price of product.")
                break
            div = change/i
            if int(div) != 0:
                print("SGD"+str(i)+": "+str(int(div)))
            sum = sum + (int(div)*i)
            change = change%i

        
        print("Sum to return: " + str(sum))
                    
if __name__== "__main__":
    main()