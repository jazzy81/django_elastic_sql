from django.shortcuts import render,redirect
from django.http import HttpResponse
from Machine.data_bases import connect_to_elasticsearch, connect_to_mysql
from datetime import datetime
from django.http import JsonResponse

def index(request):
    return render(request, 'index.html')
   

def login(request):
    if request.method == "POST":
        card_no = request.POST.get("card_no")
        pin = request.POST.get("pin")

        # Connect to Elasticsearch
        es = connect_to_elasticsearch()

        # Search for the card number and pin in Elasticsearch
        es_query = {
            "query": {
                "bool": {
                    "must": [
                        {"term": {"card_no": card_no}},
                        {"term": {"pin_no": pin}}
                    ]
                }
            }
        }

        es_response = es.search(index="data", body=es_query)
        
        if es_response['hits']['total']['value'] > 0:
            # Extract user details from Elasticsearch
            user_details = es_response['hits']['hits'][0]['_source']
            user_details.pop("pin_no", None)  # Remove the PIN from the details
            user_details['issue_date'] = datetime.strptime(user_details['issue_date'], "%Y-%m-%d")
            user_details['expiry_date'] = datetime.strptime(user_details['expiry_date'], "%Y-%m-%d")
            return render(request, "dashboard.html", {"user_details": user_details})
        else:
            # If not found in Elasticsearch, check MySQL
            try:
                db = connect_to_mysql()
                cursor = db.cursor(dictionary=True)
                query = "SELECT username, card_no, issue_date, expiry_date, balance FROM card_details WHERE card_no = %s AND pin_no = %s"
                cursor.execute(query, (card_no, pin))
                user_details = cursor.fetchone()
                user_details['issue_date'] = datetime.strptime(user_details['issue_date'], "%Y-%m-%d")
                user_details['expiry_date'] = datetime.strptime(user_details['expiry_date'], "%Y-%m-%d")
               
                if user_details:
                    return render(request, "dashboard.html", {"user_details": user_details})
                else:
                    return HttpResponse("Invalid card number or PIN.")
            except Exception as e:
                return HttpResponse(f"An error occurred: {str(e)}")
            finally:
                if db:
                    db.close()

    return render(request,"login.html")

# def withdraw(request, card_no):
    print(card_no)
    print(type(card_no))
    if request.method == "POST":
        amount = float(request.POST.get("amount", 0))
        try:
            # Connect to Elasticsearch
            es = connect_to_elasticsearch()
      
            # Retrieve the document from Elasticsearch
            es_query = {"query": {"match": {"card_no": card_no}}}
            es_response = es.search(index="data", body=es_query)

            if es_response["hits"]["total"]["value"] > 0:
                es_data = es_response["hits"]["hits"][0]
                current_balance = es_data["_source"]["balance"]

                # Ensure sufficient balance
                if current_balance >= amount:
                    new_balance = current_balance - amount

                    # Update Elasticsearch
                    es.update(
                        index="data",
                        id=es_data["_id"],
                        body={"doc": {"balance": new_balance}},
                    )

                    # Update MySQL
                    db = connect_to_mysql()
                    cursor = db.cursor()
                    mysql_query = "UPDATE card_details SET balance = %s WHERE card_no = %s"
                    cursor.execute(mysql_query, (new_balance, card_no))
                    db.commit()

                    return render(request, "withdraw.html", {"success": True, "new_balance": new_balance})
                else:
                    return render(request, "withdraw.html", {"error": "Insufficient balance."})
            else:
                return render(request, "withdraw.html", {"error": "Card not found in Elasticsearch."})
        except Exception as e:
            return render(request, "withdraw.html", {"error": f"An error occurred: {str(e)}"})
        finally:
            if db:
                db.close()
    return render(request, "withdraw.html", {"card_no": card_no})




def withdraw(request, card_no):
   
    db = None  # Initialize db as None
    if request.method == "POST":
        amount = float(request.POST.get("amount", 0))  # Ensure amount is a float
        try:
            # Connect to Elasticsearch
            es = connect_to_elasticsearch()

            # Retrieve the document from Elasticsearch
            es_query = {"query": {"match": {"card_no": card_no}}}
            es_response = es.search(index="data", body=es_query)

            current_balance_es = None  # Initialize balance
            if es_response["hits"]["total"]["value"] > 0:
                es_data = es_response["hits"]["hits"][0]
                current_balance_es = float(es_data["_source"]["balance"])  # Convert balance to float
            else:
                # If not found in Elasticsearch, retrieve balance from MySQL
                db = connect_to_mysql()
                cursor = db.cursor()
                mysql_query = "SELECT balance FROM card_details WHERE card_no = %s"
                cursor.execute(mysql_query, (card_no,))
                mysql_balance = cursor.fetchone()

                if mysql_balance:
                    current_balance_mysql = float(mysql_balance[0])  # Convert balance to float
                    current_balance_es = current_balance_mysql
                else:
                    return JsonResponse({"error": "Card not found in MySQL."})

            # Ensure sufficient balance
            if current_balance_es >= amount:
                new_balance = current_balance_es - amount

                # If found in Elasticsearch, update Elasticsearch and MySQL
                if es_response["hits"]["total"]["value"] > 0:
                    es.update(
                        index="data",
                        id=es_data["_id"],
                        body={"doc": {"balance": new_balance}},
                    )

                # Update MySQL
                if db:
                    cursor.execute("UPDATE card_details SET balance = %s WHERE card_no = %s", (new_balance, card_no))
                    db.commit()

                # Return success with new balance
                return JsonResponse({"success": True, "new_balance": new_balance})
            else:
                return JsonResponse({"error": "Insufficient balance."})

        except Exception as e:
            return JsonResponse({"error": f"An error occurred: {str(e)}"})
        finally:
            if db:  # Only close db if it was initialized
                db.close()

    return render(request, "withdraw.html", {"card_no": card_no})


from django.http import JsonResponse

def deposit(request, card_no):
    db = None  # Initialize db as None
    if request.method == "POST":
        amount = float(request.POST.get("amount", 0))  # Ensure amount is a float
        try:
            # Connect to Elasticsearch
            es = connect_to_elasticsearch()

            # Retrieve the document from Elasticsearch
            es_query = {"query": {"match": {"card_no": card_no}}}
            es_response = es.search(index="data", body=es_query)

            current_balance_es = None  # Initialize balance
            if es_response["hits"]["total"]["value"] > 0:
                es_data = es_response["hits"]["hits"][0]
                current_balance_es = float(es_data["_source"]["balance"])  # Convert balance to float
            else:
                # If not found in Elasticsearch, retrieve balance from MySQL
                db = connect_to_mysql()
                cursor = db.cursor()
                mysql_query = "SELECT balance FROM card_details WHERE card_no = %s"
                cursor.execute(mysql_query, (card_no,))
                mysql_balance = cursor.fetchone()

                if mysql_balance:
                    current_balance_mysql = float(mysql_balance[0])  # Convert balance to float
                    current_balance_es = current_balance_mysql
                else:
                    return JsonResponse({"error": "Card not found in MySQL."})

            # Add deposit amount to the current balance
            new_balance = current_balance_es + amount

            # If found in Elasticsearch, update Elasticsearch and MySQL
            if es_response["hits"]["total"]["value"] > 0:
                es.update(
                    index="data",
                    id=es_data["_id"],
                    body={"doc": {"balance": new_balance}},
                )

            # Update MySQL
            if db:
                cursor.execute("UPDATE card_details SET balance = %s WHERE card_no = %s", (new_balance, card_no))
                db.commit()

            # Return success with new balance
            return JsonResponse({"success": True, "new_balance": new_balance})

        except Exception as e:
            return JsonResponse({"error": f"An error occurred: {str(e)}"})
        finally:
            if db:  # Only close db if it was initialized
                db.close()

    return render(request, "deposit.html", {"card_no": card_no})


def logout(request):
    return redirect("login")  
