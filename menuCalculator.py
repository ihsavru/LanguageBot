#GOAL
#Imagine you have started up a small restaurant and are trying to make it easier to take and calculate orders. Since your restaurant only sells 9 different items,
# you assign each one to a number, as shown below.
# 1. Chicken Strips - $3.50
# 2. French Fries - $2.50
# 3. Hamburger - $4.00
# 4. Hotdog - $3.50
# 5. Large Drink - $1.75
# 6. Medium Drink - $1.50
# 7. Milk Shake - $2.25
# 8. Salad - $3.75
# 9. Small Drink - $1.25
#To quickly take orders, your program should allow the user to type in a string of numbers and then it should calculate the cost of the order.
#  For example, if one large drink, two small drinks, two hamburgers, one hotdog, and a salad are ordered, the user should type in 5993348,
# and the program should say that it costs $19.50. Also, make sure that the program loops so the user can take multiple orders without having to restart the program each time.
#SUBGOALS
# 1. If you decide to, print out the items and prices every time before the user types in an order.
# 2. Once the user has entered an order, print out how many of each item have been ordered, as well as the total price. If an item was not ordered at all, then it should not show up.-->

menuList = [3.5, 2.5, 4, 3.5, 1.75, 1.5, 2.25, 3.75, 1.25]
foodList = ["Chicken Strips","French Fries", "Hamburger", "Hotdog", "Large Drink", "Medium Drink", "Milk Shake", "Salad", "Small Drink"]

menu ='''1. Chicken Strips - $3.50
2. French Fries - $2.50
3. Hamburger - $4.00
4. Hotdog - $3.50
5. Large Drink - $1.75
6. Medium Drink - $1.50
7. Milk Shake - $2.25
8. Salad - $3.75
9. Small Drink - $1.25'''

while True:
    orderList = [0,0,0,0,0,0,0,0,0]
    print("MENU:")
    print(menu)
    order = input()
    cost = 0

    for item in order:
        foodItem = int(item)
        orderList[foodItem-1] = orderList[foodItem-1] + 1
        cost = cost + menuList[foodItem - 1]


    print("YOUR ORDER IS: ")
    for i in range(0,9):
        if orderList[i] > 0:
            print(orderList[i]," ",foodList[i])

    print("The total cost is", cost)




