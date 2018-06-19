import sqlite3
import sys
import getpass
import hashlib
import os
from datetime import date, datetime

connection = None
cursor = None
customer_id = None
def connect(path):
    global connection, cursor

    connection = sqlite3.connect(path)
    cursor = connection.cursor()
    cursor.execute(' PRAGMA forteign_keys=ON; ')
    connection.commit()
    return connection, cursor
def login_screen():
        os.system('clear')
        NotFound = True
        while(NotFound):
            option = input("1.customers \n2.agents \n3.exit \nYour choice: ")
            os.system('clear')
            if option == "1":
                cus_option = input("1.Login \n2.sign up \nYour choice:")
                if cus_option == '1':
                    
                    customer_login()
                if cus_option == '2':
                    
                    customer_signup()
                    customer_login()
                NotFound = False
            elif option == "2":
                
                agent_login()
                NotFound = False
            elif option == "3":
                sys.exit()
            else:
                print("Please try again.")
def main():
    global connection, cursor
    try:
        path = "./"+sys.argv[1]
        connect(path)
    except IndexError:
        path = input("Enter database's name: ")
        path = "./"+path
        connect(path)


    login_screen()


    connection.commit()
    connection.close()
    return

def customer_login():
    global connection, cursor, customer_id
    os.system('clear')
    customer_id = input("customer id: ")

    cursor.execute('SELECT * FROM customers')
    found = False
    for row in cursor.fetchall():
        if customer_id == row[0]:
            found = True
            right_password = False
            while not right_password:
                c_password = getpass.getpass("customer password:")
                c_pwd = c_password.encode('utf-8')
                hashpwd = hashlib.sha256(c_pwd)
                cursor.execute("select * from customers where cid =? and pwd = ?;", (customer_id,hashpwd.hexdigest(),))
                row = cursor.fetchone()
                if row != None:
                    print("Login successfully")
                    cursor.executescript("drop table if exists basket;create table basket(pid char(6),sid int, name TEXT,qty int,uprice real,primary key(pid,sid));")
                    right_password = True

                    customer_task()

                else:
                    print("Wrong password! Please try again. ")

    if found == False:
        print("Unregistered customers, register here!")
        customer_signup()

def customer_signup():
    global connection, cursor


    user_id = input("Please enter one user id:")
    cursor.execute('SELECT * FROM customers')
    for row in cursor.fetchall():
        if user_id == row[0]:
            print("The provided id is not unique. ")
            customer_signup()

    user_name = input("Please enter one user name:")
    user_address = input("Please enter one user address:")
    user_password = getpass.getpass("Please enter password:")
    u_pwd = user_password.encode('utf-8')
    hash_upwd = hashlib.sha256(u_pwd)

    cursor.execute("insert into customers (cid, name, address, pwd) values (?,?,?,?);", (user_id, user_name, user_address, hash_upwd.hexdigest(),))

    connection.commit()




def agent_login():
    global connection, cursor


    aid = input("agent id: ")

    while(True):
        cursor.execute("select * from agents where aid = ?;",(aid,))
        row = cursor.fetchone()
        if row != None:
            break

        else:
            print("Agent id does not exist")
            agent_login()
    correct_pwd = False
    while not correct_pwd:
        a_password = getpass.getpass("agent password: ")
        a_pwd = a_password.encode('utf-8')
        hash_apwd = hashlib.sha256(a_pwd)
        cursor.execute("select * from agents where aid = ? and pwd = ?;", (aid,  hash_apwd.hexdigest(),))
        row = cursor.fetchone()
        if row != None:
    
            print("Login successfully")

            correct_pwd = True
            agent_task()
        else:
            print("Password fail")



def customer_task():
    correct_task = False
    os.system('clear')

    while not correct_task:
        option = input("Please select your task: \n1.Search for products \n2.Place an order \n3.List orders \n4.Log out \nYour choice: ")
        if option == "1":
            search_for_products(cursor)
            correct_task = True
        elif option == "2":
            place_an_order(customer_id)
            correct_task = True
        elif option == "3":
            list_orders(customer_id)
            correct_task = True
        elif option == "4":
            cursor.execute("drop table if exists basket;")
            login_screen()
            correct_task = True
        else:
            print("Wrong task! Please try again.")

def agent_task():
    
    correct_task = False
    os.system('clear')
    while not correct_task:
        option = input("Please select your task: \n1.Set up a delivery \n2.Update a delivery \n3.Add to stock \n4.Log out \nYour choice: ")
        if option == "1":
            setup_delivery()
            correct_task = True
        elif option == "2":
            update_delivery()
            correct_task = True
        elif option == "3":
            add_to_stock()
            correct_task = True
        elif option == "4":
            login_screen()
            correct_task = True
        else:
            print("Wrong task! Please try again.")





def search_view():
    create_view =       '''
        drop view if exists search_view;
        create view search_view (pid,name,unit,number_in_store,number_in_stock,min_price_instore,min_price_instock,number_in7days,match_key)
        as select pid,name,unit,number_in_store,number_in_stock,min_price_instore,min_price_instock,number_in7days,null as match_key
        from (select c.pid,p.name,unit,count(distinct sid) as number_in_store,min(uprice) as min_price_instore 
              from products p,carries c 
              where p.pid = c.pid
              group by c.pid)
              left outer join  
              (select c.pid,count(distinct sid) as number_in_stock,min(uprice) as min_price_instock 
              from products p,carries c 
              where p.pid = c.pid and c.qty <> 0 
              group by c.pid)using (pid)
              left outer join
              (select c.pid,count(distinct olines.oid) as number_in7days
              from orders,olines,carries c
              where date(orders.odate, '+7 day') >= date('now')and olines.oid = orders.oid and olines.pid = c.pid
              group by c.pid )using(pid);


        '''
    cursor.executescript(create_view)
    
    connection.commit

# def product_detail(cursor,yourPid):
#     cursor.execute("SELECT c.pid,p.name,unit,cat,s.name,c.uprice,c.qty,order_in7days from((SELECT c.pid,p.name,unit,cat,s.name,c.uprice,c.qty from carries c, products p,store s where c.pid = p.pid and c.sid = s.sid) left outer join (select c.sid,c.pid,count(distince olines.oid) as order_in7days from olines,orders,carries c where date(orders.odate, '+7 day') >= date('now') and olines.oid = orders.oid and olines.pid = c.pid and olines.sid = c.sid)using(pid,sid)where c.pid = ? order by c.qty DESC, c.uprice ASC;",(yourPid,))
#     detailResult = cursor.fetchall()
#     print(detailResult)
def search_for_products(cursor):
    os.system('clear')
    search_view()

    checker = 0
    keywords_input = input("Please enter your keyword.(use comma to seqarate your keywords):")
    keywords = keywords_input.split(',')
    matches = 0   
    for keyword in keywords:

        cursor.execute('SELECT pid FROM search_view WHERE name LIKE ? ;', ('%'+keyword+'%',))
        hasKeyword = cursor.fetchone()
    if hasKeyword is not None:
            # matches += 1
            # for item in hasKeyword:
            #     cursor.execute("insert into search_view values match_key = ? where pid = ?;",(matches,item[0]))
            cursor.execute("SELECT pid,name,unit,number_in_store,number_in_stock,min_price_instore,min_price_instock,number_in7days from search_view where name like ? ;",('%'+keyword+'%',))
            matchProducts = cursor.fetchall()
            if len(matchProducts) <=5:
                    for i in range (0,len(matchProducts)):
                        print(matchProducts[i])
                    selectPid = input("enter pid to see more detail :")
                    cursor.execute("SELECT pid,Pname,unit,cat,Sname,Cuprice,Cqty,orderNum from((SELECT c.sid,c.pid,p.name as Pname,unit,cat,s.name as Sname,c.uprice as Cuprice, qty as Cqty from carries c, products p,stores s where c.pid = p.pid and c.sid = s.sid) left outer join (select olines.sid,olines.pid,count(*) as orderNum from olines,orders where date(orders.odate, '+7 day') >= date('now') and olines.oid = orders.oid group by olines.sid,olines.pid)using(pid,sid))where pid = ? order by Cqty DESC, Cuprice ASC;",(selectPid,))
                    detail_result = cursor.fetchall()
                    for items in detail_result:
                        print(items)
                    while(True):
                            buyoption = input("Do you want to buy any products? Y/N: ")
                            if buyoption == "Y":
                                buyProduct_pid = selectPid
                                buyProduct_name = input("Enter the store's name: ")
                                while(checker == 0):
                                    for i in range(len(detail_result)):
                                        if buyProduct_name == detail_result[i][4]:
                                            checker = 1
                                            
                                    if checker == 0:
                                        buyProduct_name = input("pid and store name not match.Enter the store's name again: ")
                                cursor.execute("SELECT sid from stores s where s.name = ?;",(buyProduct_name,))
                                sidFinder = cursor.fetchone()
                                buyProduct_sid = sidFinder[0]
                                cursor.execute("SELECT uprice from carries s where s.pid = ? and s.sid = ?;",(buyProduct_pid,buyProduct_sid,))
                                upriceFinder = cursor.fetchone()
                                buyProduct_uprice = upriceFinder[0]
                                changeQty = input("Default Quantity is 1, do you want to change? Y/N: ")
                                if changeQty == "Y":
                                    newQty = input("enter the qty you want: ")
                                    cursor.execute("INSERT INTO basket values (?,?,?,?,?);",(buyProduct_pid,buyProduct_sid,buyProduct_name,newQty,buyProduct_uprice,))
                                    connection.commit()
                                    goback = input("press B to place your order or logout: ")
                                    if goback == "B":
                                        customer_task()                                     
                                if changeQty == "N":
                                    cursor.execute("INSERT INTO basket values (?,?,?,1,?);",(buyProduct_pid,buyProduct_sid,buyProduct_name,buyProduct_uprice,))
                                    connection.commit()
                                    goback = input("press B to place your order or logout: ")
                                    if goback == "B":
                                        customer_task()                                     
                            elif buyoption == "N":
                                break
                            else:
                                print("wrong enter")      

            else:
                m = 5
                n = 0
                while(True):
                    for i in range(n,m):
                        print(matchProducts[i])
                    
                    
                    nextPage = input("press Y to see next page,press M to go to customer menu to place order or log out,enter pid to see more detail : ")

                    if nextPage == "M":
                        os.system('clear')
                        customer_task()
                    if(nextPage != "M" and nextPage != "Y"):
                        cursor.execute("SELECT pid,Pname,unit,cat,Sname,Cuprice,Cqty,orderNum from((SELECT c.sid,c.pid,p.name as Pname,unit,cat,s.name as Sname,c.uprice as Cuprice, qty as Cqty from carries c, products p,stores s where c.pid = p.pid and c.sid = s.sid) left outer join (select olines.sid,olines.pid,count(*) as orderNum from olines,orders where date(orders.odate, '+7 day') >= date('now') and olines.oid = orders.oid group by olines.sid,olines.pid)using(pid,sid))where pid = ? order by Cqty DESC, Cuprice ASC;",(nextPage,))
                        detailResult = cursor.fetchall()
                        for item in detailResult:
                             print(item)
                        
                        while(True):
                            buyoption = input("Do you want to buy any products? Y/N: ")
                            if buyoption == "Y":
                                buyProduct_pid = nextPage
                                buyProduct_name = input("Enter the store's name: ")
                                while(checker == 0):
                                    for i in range(len(detailResult)):
                                        if buyProduct_name == detailResult[i][4]:
                                            checker = 1
                                            
                                    if checker == 0:
                                        buyProduct_name = input("pid and store name not match.Enter the store's name again: ")                                
                                cursor.execute("SELECT sid from stores s where s.name = ?;",(buyProduct_name,))
                                sidFinder = cursor.fetchone()
                                buyProduct_sid = sidFinder[0]
                                cursor.execute("SELECT uprice from carries s where s.pid = ? and s.sid = ?;",(buyProduct_pid,buyProduct_sid,))
                                upriceFinder = cursor.fetchone()
                                buyProduct_uprice = upriceFinder[0]
                                
                                changeQty = input("Default Quantity is 1, do you want to change? Y/N: ")
                                if changeQty == "Y":
                                    newQty = input("enter the qty you want: ")
                                    cursor.execute("INSERT INTO basket values (?,?,?,?,?);",(buyProduct_pid,buyProduct_sid,buyProduct_name,newQty,buyProduct_uprice,))
                                    connection.commit()
                                    goback = input("press B to place your order or logout: ")
                                    if goback == "B":
                                        customer_task()    
                                    
                            
                                if changeQty == "N":
                                    cursor.execute("INSERT INTO basket values (?,?,?,1,?);",(buyProduct_pid,buyProduct_sid,buyProduct_name,buyProduct_uprice,))
                                    connection.commit()
                                    goback = input("press B to place your order or logout: ")
                                    if goback == "B":
                                        customer_task()                                     
                            elif buyoption == "N":
                                os.system('clear')
                                break
                            else:
                                print("wrong enter")    
                    if m >= len(matchProducts):
                        print("Thank you!")
                        break    

                    if nextPage == "Y":
                        n = m
                        m += 5
                        if m > len(matchProducts):
                            m = len(matchProducts)  

                    

    else:
        print("No match product")
        userSelection = input("Do you want to try again? Y/N: ")
        if userSelection == "Y":
            search_for_products(cursor)
    #  goback = input("press B to place your order or logout: ")
    #  if goback == "B":
    #      customer_task()    




#########################################################################################################


def place_an_order(cid):
    cid = cid
    
    cursor.execute('select * from olines')
    for i in cursor.fetchall():
        oid = i[0]
        unique_oid = int(oid) + 10        
    
    cursor.execute('select * from basket')
    for place_order in cursor.fetchall():
        basket_pid = place_order[0]
        basket_sid = place_order[1]
        basket_name = place_order[2]
        basket_qty = place_order[3]
        basket_uprice = place_order[4]
        cursor.execute('select * from carries where pid =? and sid =?;', (basket_pid, basket_sid))
        for qty in cursor.fetchall():
            store_qty = qty[2]
            if int(store_qty) < int(basket_qty):
                print("The store quantity for " + basket_name + " is less than the quantity in the basket")
                right_option = False
                while not right_option:
                    option = input("Type 'c' to change the quantity of the product \nType 'd' to delete the product from the basket: ")
                    if option == "c":
                        good_qty = False
                        while not good_qty:
                            change_qty = input("How many items do you want to place?")
                            if int(change_qty) <= int(store_qty):
                                good_qty = True
                                cursor.execute('UPDATE basket SET qty = ? WHERE pid = ?;', (change_qty, basket_pid))
                                connection.commit()
                        right_option = True
                    elif option == "d":
                        cursor.execute('DELETE FROM basket where pid=?;', (basket_pid,))
                        connection.commit()
                        cursor.execute('select * from basket')
                        right_option = True
                    else:
                        print("Please make your decision!")
                
    cursor.execute('select * from basket')
    if cursor.fetchone() == None:
        print("The basket is empty!")
        customer_task()
    cursor.execute('select * from basket')
    for place_order in cursor.fetchall():
            basket_pid = place_order[0]
            basket_sid = place_order[1]
            basket_qty = place_order[3]
            basket_uprice = place_order[4]    
            cursor.execute('insert into olines (oid, sid, pid, qty, uprice) values (?, ?, ?, ?, ?)', (unique_oid, basket_sid, basket_pid, basket_qty, basket_uprice))
            connection.commit()

            cursor.execute('select * from carries where pid =? and sid =?;', (basket_pid, basket_sid))
            for qty in cursor.fetchall():
                store_qty = qty[2]
                
            store_qty = store_qty - basket_qty
            cursor.execute('UPDATE carries SET qty = ? WHERE sid = ? and pid = ?;', (store_qty, basket_sid, basket_pid))
            connection.commit()    
    
    correct_address = False
    while not correct_address:
        address = input("where do you want your order to be deliveried? ")
        sure = input("Correct address? Y/N: ")
        if sure == 'Y':
            correct_address = True       
                       
    today = date.today()
    cursor.execute('insert into orders (oid, cid, odate, address) values (?, ?, ?, ?)', (unique_oid, cid, today, address))
    connection.commit()    
    print("Your order has been placed successfully!")
    print("Your order number is " + str(unique_oid))
    
    logout = input("Do you want to logout? Y/N: ")
    if logout == "Y":
        login_screen()
    else:
        customer_task() 

def list_orders(cid):
    cid = cid
    cursor.execute('select COUNT(oid) from orders where cid = ?;', (cid,))
    num = cursor.fetchone()
    number_of_orders = int(num[0])
    if number_of_orders <= 5:
        cursor.execute('select l.oid, odate, COUNT(pid)*qty as number_of_products, SUM(qty*uprice) as total_price from olines l, orders r where r.oid = l.oid and r.cid = ? group by r.oid order by odate desc, r.oid desc;', (cid,))
        for row in cursor.fetchall():
            print(row)
    else:
        m = 5
        n = 0
        cursor.execute('select l.oid, odate, COUNT(pid)*qty as number_of_products, SUM(qty*uprice) as total_price from olines l, orders r where r.oid = l.oid and r.cid = ? group by r.oid order by odate desc, r.oid desc;', (cid,))
        row = cursor.fetchall()
        while (True):
            for i in range(n, m):
                print(row[i])
                
            if m == len(row):
                print("End of the list")
                break
            
            option = input("Do you wnat to see more ? Y/N: ")
            if option == 'Y':
                n = m 
                m += 5
                if m > len(row):
                    m = len(row)
            elif option == 'N':
                break
    
    see = False
    while not see:
        detail = input("Do you want to see more detail of an order? Y/N: ")
        if detail == "Y":
            oid = input("Enter the order number of the order you want to see: ")
            print("Delivery information: ")
            cursor.execute('select trackingno, pickUpTime, dropOffTime, address from deliveries, orders where orders.oid = deliveries.oid and orders.oid = ?;', (oid,))
            d_info = cursor.fetchall()
            if d_info == []:
                print("There is no delivery information")
            else:
                print(d_info)
                
            print("Product information: ")
            cursor.execute('select o.sid, s.name, o.pid, p.name, o.qty, p.unit, o.uprice from olines o, stores s, products p where o.sid = s.sid and o.pid = p.pid and o.oid = ? group by o.pid;', (oid,))
            for row in cursor.fetchall():
                print(row)
        elif detail == "N":
            see = True
            
    logout = input("Do you want to logout? Y/N: ")
    if logout == "Y":
        login_screen()
    else:
        customer_task()    
    

#########################################################################################################

def setup_delivery():
    
    count = 0
    pickup_time = None
    dropoff_time = None
    order_list = []
    tracking_number = 0
    
    while(True):
        cursor.execute("select * from deliveries where trackingno = :tracking_number;",{"tracking_number": tracking_number}) 
        tracking_number_check = cursor.fetchone()
        if tracking_number_check != None:
            tracking_number+=1
        else:
            break
    
    print("Your tracking number is:",tracking_number)

    while(True):
        order_id = input("Please enter order id or enter s to stop:")
        if order_id == "s":
            break
        cursor.execute("select * from orders where oid = :order_id;", {"order_id": order_id})
        row = cursor.fetchone()
        if row == None:
            print("Cannot find order id.")
        else:
            count+=1
            order_list.append(order_id)
            print("order added")
            setup_pickuptime = input("Set up a pick up time?(yes/no)")
            while(setup_pickuptime != "yes" and setup_pickuptime != "no"):
                setup_pickuptime = input("Set up a pick up time?(yes/no)")
            if setup_pickuptime == "yes":
                pickup_time = input("Please enter a pick up time(yyyy-mm-dd hrs:min:sec):")
                order_list.append(pickup_time)
            else:
                order_list.append(None)

    for i in range(count): 
        value1 = order_list[i*2+1]
        value2 = order_list[(i-1)*2+2]
        cursor.execute("insert into deliveries (trackingno, oid, pickUpTime, dropOffTime) values (?,?,?,?)",(tracking_number, value2, value1, dropoff_time))
        connection.commit()
    
    agent_task()




def update_delivery():

    
    while(True):
            delivery_id = input("Please enter the tracking number:")
            cursor.execute("select * from deliveries where trackingno = :delivery_id;", {"delivery_id": delivery_id})
            rows = cursor.fetchall()
            if rows != []:
                for item in rows:
                    print(item)
                break  
            else:
                print("Cannot find delivery information.")


    while(True):
        order_id = input("Please enter the order id or enter s to stop:")
        cursor.execute("select * from deliveries where trackingno = :delivery_id and oid = :order_id;", {"delivery_id": delivery_id, "order_id": order_id})
        row = cursor.fetchone()
        if order_id == "s":
            break
        elif row != None:
            option = input("1.Update pick up time and drop of time \n2.Delete order \nEnter number to choose:")
            if option == "2":
                cursor.execute('DELETE FROM deliveries WHERE trackingno = ? and oid =?;', (delivery_id, order_id))
                connection.commit()
            elif option == "1":
                pickup_time = input("Update pick up time(yyyy-mm-dd hr:min:sec):")
                dropoff_time = input("Update drop off time(yyyy-mm-dd hr:min:sec):")
                sql = '''update deliveries
                    set pickUpTime = ?, dropOffTime = ?
                    where trackingno = ? and oid = ?;'''
                cursor.execute(sql, (pickup_time, dropoff_time, delivery_id, order_id)) 
                connection.commit()
        else:
            print("Cannot find order")
    
    agent_task()




def add_to_stock():

    product_id = input("Enter selected product id:")
    store_id = input("Enter selected store id:")
    add_number = input("number of product to be added:")
    option = input("Change the unit price?(yes/no):")
    while(option != "yes" and option != "no"):
        option = input("Change the unit price?(yes/no):")
    cursor.execute("select * from carries where sid = ? and pid = ?;",(store_id,product_id))
    row = cursor.fetchone()
    if row == None:
        if option == "yes":
            unit_price = input("Enter Unit price:")
            cursor.execute("insert into carries (sid, pid, qty, uprice) values (?,?,?,?)", (store_id, product_id, add_number, unit_price))
            connection.commit()
        else:
            cursor.execute("insert into carries (sid, pid, qty, uprice) values (?,?,?,?)", (store_id, product_id, add_number, None))
            connection.commit()



    else:
        cursor.execute("select qty from carries where sid = ? and pid = ?;",(store_id,product_id))
        row = cursor.fetchone()
        stock_number = row[0]

        final_number = int(add_number) + int(stock_number)



        update_1 = '''update carries
                    set qty = ?, uprice = ?
                    where sid = ? and pid = ?;'''

        update_2 = '''update carries
                    set qty = ?
                    where sid = ? and pid = ?;'''


        if option == "yes":
            unit_price = input("Enter Unit price:")
            cursor.execute(update_1, (final_number, unit_price, store_id, product_id))
            connection.commit()
        else:
            cursor.execute(update_2, (final_number, store_id, product_id))
            connection.commit()
    
    print("Adding successfully")
    agent_task()


            



if __name__ == "__main__":
    main()
