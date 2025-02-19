import json
import os
import requests
from bs4 import BeautifulSoup
import sys
from datetime import datetime

server_url = "http://172.18.6.10:5000/update-EBike-json"

# Path to your JSON file
# json_file_path = "Ebike_server_data.json"

def send_json_data(json_data, Repo):
    """ Send JSON data to the server """
    try:
        payload = {"Repo": Repo, "data": json_data}
        response = requests.post(server_url, json=payload)
        if response.status_code == 200:
            print("JSON sent successfully")
        else:
            print("Failed to send JSON:", response.status_code, response.json())
    except Exception as e:
        print("An error occurred:", str(e))


def save_build_data(data, file_path):
    """ Save JSON data to a file """
    with open(file_path, 'w') as file:
        json.dump(data, file, indent=4)

def filter_pr_lines(pr_list_file):
    """ Filter lines containing # from the Git log output safely """
    try:
        with open(pr_list_file, 'r') as file:
            prs_list = file.read().replace('\t', '  ').split('\n')
        if len(prs_list) > 4:
            return "<pre>" + "<br>".join(prs_list[3:-4]) + "</pre>", prs_list[6].split(":")[-1]
        return "<pre>" + "<br>".join(prs_list) + "</pre>",prs_list[6].split(":")[-1]
    except Exception as e:
        print(f"Error reading PR file {pr_list_file}: {e}")
        return "<pre>Error loading PRs</pre>"

def fetch_build_data(base_url):
    """ Fetch the latest build data from the given URL """
    build_data = {}
    latest_date = None
    latest_url = None
    response = requests.get(base_url)
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        rows = soup.find_all('tr')
        
        for row in rows:
            link = row.find('a')
            if link:
                href = link.get('href')
                if href and (href.endswith('.7z') or href.endswith('.zip')):
                    full_url = base_url + href
                    date_td = link.find_next('td')
                    date = date_td.text.strip() if date_td else 'N/A'

                    # Convert date into desired format if valid
                    try:
                        date_obj = datetime.strptime(date, '%Y-%m-%d %H:%M')
                        formatted_date = date_obj.strftime('%Y-%m-%d %H:%M')
                    except ValueError:
                        formatted_date = 'N/A'

                    # Check if this file has the most recent date
                    if not latest_date or formatted_date > latest_date:
                        latest_date = formatted_date
                        latest_url = full_url
                        file_name = href

        # Store the latest .7z file URL and its corresponding date
        if latest_url:
            build_data = {
                "file_name": file_name,
                "name_of_the_link": latest_url,
                "date_time": latest_date
            }

    return build_data

if __name__ == '__main__':
    print("Check the server URL:", server_url)
    Repo = input("Enter the repo name: ")
    # Repo = sys.argv[1]
    print(f"Repository Name: {Repo}")
    # URLs for fetching build data
    AURIGA_BP_Artifact_url = "http://172.18.7.60/ramp/ebike_artifact/AURIGA_BP/"
    AURIGA_YP_Artifact_url = "http://172.18.7.60/ramp/ebike_artifact/PTG_BIKE_YP/"
    DOL_MOTORS_YP_Artifact_url = "http://172.18.7.60/ramp/ebike_artifact/PTG_BIKE_YP_DOL/"

    
    pr_list_DOL_MOTORS_YP = "static/pr_list_DOL_MOTORS_YP.txt"
    pr_list_AURIGA_BP = "static/pr_list_AURIGA_BP.txt"
    pr_list_AURIGA_YP = "static/pr_list_AURIGA_YP.txt"

    APK_url_hmi = "http://172.18.7.60/ramp/ebike_artifact/AURIGA_APK/Auriga/"
    APK_url_android = "http://172.18.7.60/ramp/ebike_artifact/AURIGA_APK/E-BikeMobile/"
    # Fetch latest build data

    if Repo == "DOL_MOTORS_YP":
        Artifact_data = fetch_build_data(DOL_MOTORS_YP_Artifact_url)
        pr_list,APK_IOS = filter_pr_lines(pr_list_DOL_MOTORS_YP)
        APK_url_hmi = "http://172.18.7.60/ramp/ebike_artifact/DOL_APK/Auriga/"
        APK_url_android = "http://172.18.7.60/ramp/ebike_artifact/DOL_APK/E-BikeMobile/"
    elif Repo == "AURIGA_BP":
        Artifact_data = fetch_build_data(AURIGA_BP_Artifact_url)
        pr_list,APK_IOS = filter_pr_lines(pr_list_AURIGA_BP)
    elif Repo == "AURIGA_YP":
        Artifact_data = fetch_build_data(AURIGA_YP_Artifact_url)
        pr_list,APK_IOS = filter_pr_lines(pr_list_AURIGA_YP)

    HMI_APK_data = fetch_build_data(APK_url_hmi)
    Android_APK_data = fetch_build_data(APK_url_android)
    # APK_data = fetch_build_data(APK_url)
    

    # Prepare final data structure
    final_data = {
        "Artifact_Name": Artifact_data.get("file_name", "N/A"),
        "Artifact": Artifact_data.get("name_of_the_link", "N/A"),
        "HMI_APK": HMI_APK_data.get("name_of_the_link", "N/A"),
        "Android_APK": Android_APK_data.get("name_of_the_link", "N/A"),
        "IOS_APK": APK_IOS,
        "date_time": Artifact_data.get("date_time", "N/A"),
        "PRs": pr_list
    }
    updated_data = [final_data["Artifact_Name"], final_data["Artifact"], final_data["HMI_APK"], final_data["Android_APK"], final_data["IOS_APK"], final_data["date_time"], final_data["PRs"]]

    # Send updated data to the server
    send_json_data(updated_data,Repo)

    print("Data sent successfully")
