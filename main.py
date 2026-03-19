import random
import json
import matplotlib.pyplot as plt

#Retourne la liste des prix d'entree
def load_prices(positions) -> list[tuple[float, int]] | None:
	if (positions is None):
		return (None)
	prices: list[tuple[float, int]] = [
		[0.90, 0],
		[0.91, 0],
		[0.92, 0],
		[0.93, 0],
		[0.94, 0],
		[0.95, 0],
		[0.96, 0],
		[0.97, 0],
		[0.98, 0],
		[0.99, 0]
	]
	for pos in positions:
		for p in prices:
			if p[0] <= pos['entry_price'] < p[0] + 0.01:
				p[1] += 1
				break
	return (prices)

def load_nb_trades(positions, prices) -> int:
	sum_trades: int = 0
	for p in prices:
		sum_trades += p[1]
	if (sum_trades != len(positions)):
		return (-1)
	return (len(positions))

def load_winrate(positions) -> float:
	win: int = 0
	lost: int = 0
	other: int = 0
	for pos in positions:
		if (pos['won'] == True):
			win += 1
		elif (pos['won'] == False):
			lost += 1
		else:
			other += 1
	return (float(float(win)/float(win + lost)))

def generate_realistic_price(prices, nb_trades) -> float:
	random_pick: int = random.randint(1, nb_trades)
	total_count: int = 0
	for p in prices:
		if (total_count < random_pick <= total_count + p[1]):
			return (p[0])
		total_count += p[1]
try:
	file = open("trades.json", encoding="utf-8")
except:
	file_path: str = str(input("\nEntrez le path vers le fichier de sauvegarde .json : "))
	try:
		file = open(file_path, encoding="utf-8")
	except:
		print(f"ERROR : Le fichier {file_path} n'existe pas ou n'autorise pas la lecture.")
		exit()
file_json = json.load(file)
positions = file_json['positions']
if (positions is None or len(positions) == 0):
	if (positions is None):
		print(f"ERROR : Impossible de charger {file_path}.")
	elif (len(positions) == 0):
		print(f"ERROR : Le fichier {file_path} ne contient aucun trades.")
	exit()

prices: list[tuple[float, int]] = load_prices(positions)
if (prices is None):
	print(f"ERROR : Impossible de charger les trades depuis {file_path}.")
	exit()

number_trades: int = load_nb_trades(positions, prices)
winrate: float = load_winrate(positions)

if (number_trades == -1 or winrate == -1):
	if (number_trades == -1):
		print(f"ERROR : Nombre de trades incoherent entre prices et {file_path}.")
	elif (winrate == -1):
		print(f"ERROR : Impossible de charger le winrate depuis {file_path}.")
	exit()

print("====================== ANALYSE DE LA SAUVEGARDE =======================")
print(f"Nombre de trades effectues    : {number_trades}.")
print(f"Winrate des positions prises  : {(winrate * 100):.2f}%")
print(f"Repartition des prix d'entree :")
for p in prices:
	print(f"	- {p[0]:.2f}$ : {p[1]:6} ({((float(p[1])/float(number_trades)) * 100):.2f}%)")

initial_cash: float = float(input("\nEntrez la somme de depart                          : "))
if initial_cash <= 0:
	if (initial_cash == 0):
		print("ERROR : Le cash de depart ne peut pas etre nul.")
	if (initial_cash < 0):
		print("ERROR : Le cash de depart ne peut pas etre negatif.")
	exit()
bet_percent: int = int(input("Entrez le pourcentage de la somme mise par pari    : "))
if (bet_percent <= 0 or bet_percent > 100):
	if (bet_percent == 0):
		print("ERROR : Le pourcentage mise par pari ne peut pas etre nul.")
	if (bet_percent < 0):
		print("ERROR : Le pourcentage mise par pari ne peut pas etre negatif.")
	if (bet_percent == 0):
		print("ERROR : Le pourcentage mise par pari ne peut pas etre superieur a 100%.")
	exit()
bet_rate: float = float(float(bet_percent) / float(100))
windows: int = int(input("Entrez le nombre de paris sur la periode a simuler : "))
if (windows <= 0):
	if (windows == 0):
		print("ERROR : Le nombre de paris par periode ne peut pas etre nul.")
	if (windows < 0):
		print("ERROR : Le nombre de paris par periode ne peut pas etre negatif.")
	exit()
nb_simulations: int = int(input("Entrez le nombre de simulations a lancer           : "))
if (nb_simulations <= 0):
	if (nb_simulations == 0):
		print("ERROR : Le nombre de simulations ne peut pas etre nul.")
	if (nb_simulations < 0):
		print("ERROR : Le nombre de simulations ne peut pas etre negatif.")
	exit()

print("\n============================= SIMULATION ==============================")
sim_max: float = -1
sim_min: float = 10000000000
sim_total: float = 0
sim_win: int = 0
sim_draw: int = 0
sim_loss: int = 0
simulations_results: list[float] = []

for i in range(0, nb_simulations): #Pour chaque simulation
	bar_percent = (i / (nb_simulations - 1)) * 100
	bar = "■" * int(bar_percent / 2) + "▢" * (50 - int(bar_percent / 2))
	print(f"\r{bar_percent:.2f}% - {bar}          ", end="", flush=True)
	cash = initial_cash
	for j in range(0, windows): #Pour chaque trade effectue
		mise: float = cash * bet_rate
		win_random: float = random.random()
		if (win_random <= winrate): #En cas de WIN
			entry_price: float = generate_realistic_price(prices, number_trades)
			gain: float = mise / entry_price
			cash += gain - mise
		else: #En cas de LOSS
			cash -= mise
	sim_total += cash
	simulations_results.append(cash)
	if (cash > sim_max):
		sim_max = cash
	if (cash < sim_min):
		sim_min = cash
	if (cash > initial_cash):
		sim_win += 1
	elif (cash < initial_cash):
		sim_loss += 1
	else:
		sim_draw += 1

sim_mean: float = float(float(sim_total) / float(nb_simulations))
simulations_results.sort()
sim_d1: float = simulations_results[int(float(float(nb_simulations)/float(10)))]
sim_q1: float = simulations_results[int(float(float(nb_simulations)/float(4)))]
sim_med: float = simulations_results[int(float(float(nb_simulations)/float(2)))]
sim_q3: float = simulations_results[int(float(float(nb_simulations)/float(4)) * 3)]
sim_d9: float = simulations_results[int(float(float(nb_simulations)/float(10)) * 9)]

# x = [i / (len(simulations_results) - 1) * 100 for i in range(len(simulations_results))]
# y = simulations_results
# renta_line = next((i for i, sim in enumerate(simulations_results) if sim >= initial_cash), None)

# plt.style.use("dark_background")
# plt.plot(x, y, color="red", label="Prix")
# plt.axhline(y=initial_cash, color="blue", linestyle="--", label="Cash de depart")
# if renta_line is not None:
# 	renta_percent = renta_line / (len(simulations_results) - 1) * 100
# 	plt.axvline(x=renta_percent, color="green", linestyle=":", label="Debut rentabilite")
# plt.xlabel("Classement de la simulation (en %)")
# plt.ylabel("Prix (en $)")
# plt.title(f"Projections sur la base de l'historique apres {nb_simulations} simulations")
# plt.legend()
# plt.grid()
# plt.tight_layout(rect=[0, 0, 0.84, 1])
# plt.savefig("projections.png", dpi=150)

x = [i / (len(simulations_results) - 1) * 100 for i in range(len(simulations_results))]
y = simulations_results
renta_line = next((i for i, sim in enumerate(simulations_results) if sim >= initial_cash), None)

fig, ax = plt.subplots(figsize=(14, 8))
fig.patch.set_facecolor("#0f1117")
ax.set_facecolor("#171b26")

# Courbe principale
ax.plot(
	x,
	y,
	color="#ff4d4d",
	linewidth=2.4,
	label="Résultat des simulations",
	zorder=3
)

# Ligne cash initial
ax.axhline(
	y=initial_cash,
	color="#4da6ff",
	linestyle="--",
	linewidth=1.8,
	label="Cash de départ",
	zorder=2
)

# Ligne début de rentabilité
if renta_line is not None:
	renta_percent = renta_line / (len(simulations_results) - 1) * 100
	ax.axvline(
		x=renta_percent,
		color="#3ddc97",
		linestyle=":",
		linewidth=2,
		label="Début rentabilité",
		zorder=2
	)

# Zones de couleur par rapport au cash initial
ax.fill_between(
	x, y, initial_cash,
	where=[v >= initial_cash for v in y],
	interpolate=True,
	alpha=0.18,
	color="#3ddc97",
	zorder=1
)

ax.fill_between(
	x, y, initial_cash,
	where=[v < initial_cash for v in y],
	interpolate=True,
	alpha=0.18,
	color="#ff4d4d",
	zorder=1
)

# Points remarquables
x_min = x[0]
x_q1 = 25
x_med = 50
x_q3 = 75
x_max = x[-1]

ax.scatter([x_min], [sim_min], color="#ff6b6b", s=45, zorder=4)
ax.scatter([x_med], [sim_med], color="#ffd166", s=55, zorder=4)
ax.scatter([x_max], [sim_max], color="#06d6a0", s=45, zorder=4)

# Annotations
ax.annotate(
	f"Min\n{sim_min:.2f}$",
	xy=(x_min, sim_min),
	xytext=(8, -18),
	textcoords="offset points",
	color="white",
	fontsize=9,
	bbox=dict(boxstyle="round,pad=0.25", fc="#222735", ec="none", alpha=0.9)
)

ax.annotate(
	f"Médiane\n{sim_med:.2f}$",
	xy=(x_med, sim_med),
	xytext=(8, 12),
	textcoords="offset points",
	color="white",
	fontsize=9,
	bbox=dict(boxstyle="round,pad=0.25", fc="#222735", ec="none", alpha=0.9)
)

ax.annotate(
	f"Max\n{sim_max:.2f}$",
	xy=(x_max, sim_max),
	xytext=(-65, 12),
	textcoords="offset points",
	color="white",
	fontsize=9,
	bbox=dict(boxstyle="round,pad=0.25", fc="#222735", ec="none", alpha=0.9)
)

if renta_line is not None:
	ax.annotate(
		f"Rentable à partir de {renta_percent:.2f}%",
		xy=(renta_percent, initial_cash),
		xytext=(10, 18),
		textcoords="offset points",
		color="white",
		fontsize=9,
		bbox=dict(boxstyle="round,pad=0.25", fc="#1f2a1f", ec="none", alpha=0.9)
	)

# Quartiles visuels
for xpos, label in [(10, "D1"), (25, "Q1"), (50, "Q2"), (75, "Q3"), (90, "D9")]:
	ax.axvline(x=xpos, color="white", linestyle=":", linewidth=0.8, alpha=0.12, zorder=0)
	ax.text(
		xpos,
		ax.get_ylim()[0],
		f" {label}",
		color="white",
		alpha=0.45,
		fontsize=8,
		va="bottom"
	)

# Titres et labels
ax.set_title(
	f"Projection Monte Carlo sur {nb_simulations} simulations avec {initial_cash}$ de depart",
	color="white",
	fontsize=16,
	fontweight="bold",
	pad=16
)
ax.set_xlabel("Classement des simulations (%)", color="white", fontsize=11)
ax.set_ylabel("Capital final ($)", color="white", fontsize=11)

# Axe X propre
ax.set_xlim(0, 100)
ax.set_xticks([0, 10, 25, 50, 75, 90, 100])
ax.set_xticklabels(["0%", "10%", "25%", "50%", "75%", "90%", "100%"], color="white")

# Style axes
ax.tick_params(axis="y", colors="white")
for spine in ax.spines.values():
	spine.set_color("#3a3f4b")

ax.grid(True, linestyle="--", linewidth=0.7, alpha=0.18)

# Légende
legend = ax.legend(
	loc="upper left",
	frameon=True,
	facecolor="#222735",
	edgecolor="#3a3f4b",
	labelcolor="white"
)
for text in legend.get_texts():
	text.set_color("white")

plt.tight_layout()
plt.savefig("projections.png", dpi=180, facecolor=fig.get_facecolor())

print("\n============================== RESULTATS ==============================")
print(f"Nombre de simulations effectuees         : {nb_simulations}")
print(f"Pourcentage de simulations WIN/DRAW/LOSS : {(sim_win / nb_simulations * 100):04.2f}% / {(sim_draw/nb_simulations * 100):04.2f}% / {(sim_loss/nb_simulations * 100):04.2f}%")
print(f"Moyenne           : {sim_mean:.2f}$ ({((sim_mean / initial_cash * 100) - 100):+.2f}%)")
print(f"Pire resultat     : {sim_min:.2f}$ ({((sim_min / initial_cash * 100) - 100):+.2f}%)")
print(f"D1 (Bottom 10%)   : {sim_d1:.2f}$ ({((sim_d1 / initial_cash * 100) - 100):+.2f}%)")
print(f"Q1 (Bottom 25%)   : {sim_q1:.2f}$ ({((sim_q1 / initial_cash * 100) - 100):+.2f}%)")
print(f"Q2 (Mid)          : {sim_med:.2f}$ ({((sim_med / initial_cash * 100) - 100):+.2f}%)")
print(f"Q3 (Top 25%)      : {sim_q3:.2f}$ ({((sim_q3 / initial_cash * 100) - 100):+.2f}%)")
print(f"D9 (Top 10%)      : {sim_d9:.2f}$ ({((sim_d9 / initial_cash * 100) - 100):+.2f}%)")
print(f"Meilleur resultat : {sim_max:.2f}$ ({((sim_max / initial_cash * 100) - 100):+.2f}%)\n")
plt.show()
print("Graphique enregistre sous : \"projections.png\"")