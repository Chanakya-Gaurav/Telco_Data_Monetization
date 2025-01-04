import plotly.express as px

df = px.data.gapminder().query("continent == 'Oceania'")
print(df)
fig = px.bar(df, x='year', y='pop',
             hover_data=['lifeExp', 'gdpPercap'], color='country',
             labels={'pop':'population of Canada'}, height=400)
fig.show()
