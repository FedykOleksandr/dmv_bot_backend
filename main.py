import time
import requests


def get_available_dates(branch_id):
    # Створіть URL для запиту, включаючи branch_id
    url = f"https://www.dmv.ca.gov/portal/wp-json/dmv/v1/appointment/branches/{branch_id}/dates?services[]=DT!1857a62125c4425a24d85aceac6726cb8df3687d47b03b692e27bd8d17814&numberOfCustomers=1&ver=650499006111.7792"
    response = requests.get(url)
    if response.status_code == 200:
        dates = response.json()
        print("Available dates for branch_id" + branch_id)
        print(dates)
        return [date.split('T')[0] for date in dates]
    else:
        return []


def main():
    get_available_dates("537!f851dc91008db76688d659c88058b9032eb5887bc63e78f0d415736861df")
    time.sleep(3)
    get_available_dates("587!a851adb5d504571f5f90bdd8ca2eeff4a9ef3d223f35667eb1f21b6ee3d4")
    time.sleep(3)
    get_available_dates("661!ddecb9e0380793634b1b679218bd2f93de6555567ba2ef61b195efdf28c5")


if __name__ == "__main__":
    main()
