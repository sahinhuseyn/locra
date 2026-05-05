import osmnx as ox
import pyproj

centers = {
    "Nasimi, Baku, Azerbaijan":   (40.3777, 49.8520),
    "Sabail, Baku, Azerbaijan":   (40.3653, 49.8379),
    "Xətai, Baku, Azerbaijan":    (40.3769, 49.8910),
    "Binagadi, Baku, Azerbaijan": (40.4380, 49.8560),
}

def get_score(city):
    try:
        tags = {"amenity": True}
        pois = ox.features_from_place(city, tags=tags)
        amenities = pois["amenity"].value_counts()

        def get_count(cat):
            return int(amenities.get(cat, 0))

        def score(count, ideal):
            return min(round(count / ideal * 100), 100)

        scores = {
            "məktəb":    score(get_count("school"),   50),
            "xəstəxana": score(get_count("hospital"), 60),
            "aptek":     score(get_count("pharmacy"), 50),
            "kafe":      score(get_count("cafe"),    150),
            "bank/ATM":  score(get_count("bank") + get_count("atm"), 100),
        }

        # Metro məsafəsi skoru
        try:
            lat, lon = centers[city]

            metro_tags = {"railway": "station", "station": "subway"}
            metro = ox.features_from_point((lat, lon), tags=metro_tags, dist=3000)

            if len(metro) > 0:
                metro_proj = metro.geometry.to_crs("EPSG:32638")
                center_x, center_y = pyproj.Transformer.from_crs(
                    "EPSG:4326", "EPSG:32638", always_xy=True
                ).transform(lon, lat)

                distances = metro_proj.centroid.apply(
                    lambda p: ((p.x - center_x)**2 + (p.y - center_y)**2)**0.5
                )
                min_dist = distances.min()
                metro_score = max(0, min(100, round(100 - min_dist / 200)))
                scores["metro"] = metro_score
            else:
                scores["metro"] = 0
        except Exception as e:
            print(f"  metro xətası: {e}")
            scores["metro"] = 0

        return scores

    except Exception as e:
        print(f"Xəta: {city} — {e}")
        return None


neighborhoods = {
    "Nəsimi":   "Nasimi, Baku, Azerbaijan",
    "Səbail":   "Sabail, Baku, Azerbaijan",
    "Xətai":    "Xətai, Baku, Azerbaijan",
    "Binəqədi": "Binagadi, Baku, Azerbaijan",
}

results = {}
for name, query in neighborhoods.items():
    print(f"{name} çəkilir...")
    results[name] = get_score(query)

cats = ["məktəb", "xəstəxana", "aptek", "kafe", "bank/ATM", "metro"]

print("\n" + "=" * 65)
print(f"{'LOCRA':<12}", end="")
for c in cats:
    print(f"{c:>10}", end="")
print(f"{'ÜMUMI':>8}")
print("=" * 65)

for name, scores in results.items():
    if scores:
        total = round(sum(scores.values()) / len(scores))
        print(f"{name:<12}", end="")
        for c in cats:
            print(f"{scores.get(c, 0):>10}", end="")
        print(f"{total:>8}")



import json

output = {}
for name, query in neighborhoods.items():
    data = results.get(name)
    if data:
        nb_coords = {
            "Nəsimi":    {"lat": 40.3777, "lon": 49.8520},
            "Səbail":    {"lat": 40.3453, "lon": 49.8279},
            "Xətai":     {"lat": 40.3869, "lon": 49.9010},
            "Binəqədi":  {"lat": 40.4580, "lon": 49.8460},
        }
        output[name] = {
            "lat": nb_coords[name]["lat"],
            "lon": nb_coords[name]["lon"],
            **data,
            "ümumi": round(sum(data.values()) / len(data))
        }

with open("scores.json", "w", encoding="utf-8") as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print("\nscores.json saxlanıldı!")