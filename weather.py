import json
import urllib.request


CITIES_FILE = "Cities.txt"
OUTPUT_FILE = "output.txt"
API_URL = "https://wttr.in/{city}?format=j1"
REQUEST_TIMEOUT = 20


class WeatherData:
    def __init__(self, city, temp_c, country):
        self.city = city
        self.temp_c = temp_c
        self.country = country


def load_cities(path):
    with open(path, encoding="utf-8-sig") as f:
        cities = [line.strip() for line in f if line.strip()]
    return list(dict.fromkeys(cities))


def fetch_weather(city):
    url = API_URL.format(city=city.replace(" ", "+"))
    with urllib.request.urlopen(url, timeout=REQUEST_TIMEOUT) as resp:
        return json.loads(resp.read().decode("utf-8"))


def parse_weather(city, data):
    temp_c = int(data["current_condition"][0]["temp_C"])
    country = data["nearest_area"][0]["country"][0]["value"]
    return WeatherData(city, temp_c, country)


def format_temp(t):
    return f"{t:+d} °C"


def main():
    cities = load_cities(CITIES_FILE)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as out:
        def write(line=""):
            print(line)
            print(line, file=out)

        results = []
        for city in cities:
            try:
                weather = parse_weather(city, fetch_weather(city))
            except (OSError, ValueError, KeyError, IndexError) as e:
                write(f"{city}: не удалось получить данные ({e})")
                continue
            results.append(weather)
            write(f"{weather.city}, {weather.country} {format_temp(weather.temp_c)}")

        groups = {}
        for w in results:
            groups.setdefault(w.country, []).append(w.temp_c)

        write()
        for country, temps in groups.items():
            avg = round(sum(temps) / len(temps))
            write(f"{country} — {len(temps)} cities, avg: {format_temp(avg)}, "
                  f"min: {format_temp(min(temps))}, max: {format_temp(max(temps))}")


if __name__ == "__main__":
    main()
