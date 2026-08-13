import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# 1. Chargement
df = sns.load_dataset("iris")

# 2. Exploration
print(df.head())
print(df.info())

# 3. Nettoyage
df = df.dropna()

# 4. Analyse
print(df.describe())

# 5. Visualisation
sns.scatterplot(
    x="sepal_length",
    y="sepal_width",
    data=df
)

plt.title("Relation entre longueur et largeur des sépales")
plt.show()

# 6. Préparation ML
X = df.drop("species", axis=1)
y = df["species"]