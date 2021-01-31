# %%
from itertools import combinations
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib import gridspec

from sklearn.linear_model import ElasticNet, Lasso, LinearRegression, LogisticRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.decomposition import PCA


# %%
DATA_FILE_PATH = 'StudentsPerformance.csv'

data_raw = pd.read_csv(filepath_or_buffer=DATA_FILE_PATH)
data_raw = data_raw.dropna()
data_raw.head()

# %%
data_raw.shape

# %%
data_raw.describe()

# %%

for column in data_raw.columns:
    if(data_raw[column].dtype == np.object_):
        print(f"Unique values of '{column}':\n {data_raw[column].unique()}\n")

# %%
data_raw.dtypes
# %%
# %%
for col in data_raw.columns:
    if(data_raw[col].dtype != np.object_):
        q_low = data_raw[col].quantile(0.01)
        q_hi = data_raw[col].quantile(0.99)
        outliers = data_raw[(data_raw[col] > q_hi) | (data_raw[col] < q_low)]
        if len(outliers) > 0:
            print(
                f'column: {col}, outliers:\n{[val for val in outliers[col]]}')
        else:
            print(f'column: {col}, no outliers')
    else:
        print(f'column: {col}, no outliers')

# %%
le = LabelEncoder()
data_encoded = data_raw.copy()

for column in data_encoded.columns:
    if(data_encoded[column].dtype == np.object_):
        le.fit(data_encoded[column])
        data_encoded[column] = le.transform(data_encoded[column])

data_encoded.head()

# %%
data_encoded.describe()

# %%
data_encoded.describe().isnull()


# %%
corr = data_encoded.corr()
sns.heatmap(data=corr, square=True, linewidths=.5,
            cmap='rocket_r').set_title('Correlation Matrix')


# %%
sns.heatmap(data=abs(corr), square=True, linewidths=.5,
            cmap='rocket_r').set_title('Absolute Correlation Matrix')

# %%

fig = plt.figure(figsize=(15, 6))

gs = gridspec.GridSpec(1, 3, width_ratios=[1, 2, 1])
ax = plt.subplot(gs[0])
sns.barplot(ax=ax,
            x=data_raw['gender'].value_counts().index,
            y=data_raw['gender'].value_counts().values, palette='rocket', alpha=.8)
sns.despine(left=True)

ax = plt.subplot(gs[1])
sns.barplot(ax=ax,
            x=data_raw['race/ethnicity'].value_counts().index,
            y=data_raw['race/ethnicity'].value_counts().values, palette='mako', alpha=.8)
sns.despine(left=True)

ax = plt.subplot(gs[2])
sns.barplot(ax=ax,
            x=data_raw['lunch'].value_counts().index,
            y=data_raw['lunch'].value_counts().values, palette='mako', alpha=.8)
sns.despine(left=True)
fig.text(0.075, 0.5, "Occurrencies count", rotation="vertical", va="center")

# %%
data_plot = data_raw.copy()
data_plot.sort_values(by=['math score'], inplace=True)
g = sns.catplot(
    data=data_plot, x='gender',  y='math score', hue='parental level of education',
    kind='bar', palette='rocket', alpha=.8)


# %%

sns.lmplot(data=data_plot, x='writing score', y='math score', hue='gender',
           hue_order=['male', 'female'], height=10, aspect=1.5,  scatter_kws={'alpha': 0.5})

# %%
data_plot['total score'] = data_plot['math score'] + \
    data_plot['reading score'] + data_plot['writing score']
data_plot.sort_values(by=['total score'], inplace=True)


fig, ax = plt.subplots(figsize=(24, 12))
sns.set(font_scale=1.5, style='whitegrid')
sns.violinplot(ax=ax, data=data_plot, x='race/ethnicity', y='total score',
               hue='lunch', inner='quart', split=True, figsize=(22, 12))
sns.despine(left=True, bottom=True)

# %%


class Model:

    def __init__(self, model, data: pd.DataFrame, target_label: str, include: list = [], test_size: float = 0.25, seed: int = None, **model_params: any) -> None:
        self.model = model(
            **model_params) if isinstance(model, type) else model
        self.test_size = test_size
        self.seed = seed
        self.data = data.copy()
        self.accuracy_cv = []
        self.accuracy = 0
        self.accuracies = {}
        self.target_label = target_label
        self.cv = 5
        self.set_data(include=include)

    def set_data(self, data: pd.DataFrame = None, target_label: str = None, include: list = []) -> None:
        self.X = data or self.data.copy()
        self.Y = self.X.pop(target_label or self.target_label)
        if include:
            self.X = self.X[include]

        scaler = StandardScaler().fit(self.X)
        self.X = scaler.transform(self.X)

        # pca = PCA(n_components=min(4, len(include))).fit(self.X)
        # self.X = pca.transform(self.X)

        self.X_train, self.X_test, self.Y_train, self.Y_test = train_test_split(
            self.X, self.Y, test_size=self.test_size, random_state=self.seed)

    def find_optimal_columns(self, score_func: callable) -> tuple:
        self.accuracies = {}
        columns = list(self.data.columns)
        columns.remove(self.target_label)

        for combination_length in range(1, len(columns)+1):
            for combination in combinations(columns, combination_length):
                self.set_data(include=list(combination))
                self.accuracies[combination] = score_func()
        optimal_columns = max(self.accuracies, key=self.accuracies.get)
        print(f'\nModel: {type(self.model).__name__}')
        print(f'Optimal columns: {optimal_columns}')
        print(
            f'Mean {self.cv}-fold accuracy: {self.accuracies[optimal_columns]}')
        return optimal_columns

    def score_cv(self, cv: int = None, **params: any) -> list:
        self.accuracy_cv = cross_val_score(
            self.model, self.X, self.Y, cv=cv or self.cv, **params)
        mean_accuracy_cv = np.mean(self.accuracy_cv)
        return mean_accuracy_cv

    def score(self):
        self.model = self.model.fit(self.X_train, self.Y_train)
        self.accuracy = self.model.score(self.X_test, self.Y_test)
        print(f'\nModel: {type(self.model).__name__}')
        print(f'Accuracy: {self.accuracy}')
        return self.accuracy


target_label = 'math score'
seed = 0
models = [LinearRegression, Lasso(alpha=0.5), RandomForestRegressor(
    max_depth=10), ElasticNet(alpha=0.5)]

for model in models:
    m = Model(model, data_encoded, target_label, seed=seed)
    m.find_optimal_columns(score_func=m.score_cv)


# %%

target_label = 'gender'
seed = 0
lm = Model(LogisticRegression, data_encoded, target_label, seed=seed)
_ = lm.find_optimal_columns(score_func=lm.score_cv)

# %%
