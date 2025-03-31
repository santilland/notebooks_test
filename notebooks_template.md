# 📚 Notebook Catalog

```{raw} html
<style>
.catalog-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 20px;
    padding: 20px;
}
.catalog-item {
    border: 1px solid #ddd;
    border-radius: 10px;
    padding: 15px;
    text-align: center;
    background-color: #f9f9f9;
    transition: transform 0.2s;
}
.catalog-item:hover {
    transform: scale(1.05);
}
.catalog-item img {
    max-width: 80px;
    margin-bottom: 10px;
}
</style>
<div class="catalog-grid">
{% for notebook in notebooks %}
    <div class="catalog-item">
        <img src="https://img.icons8.com/ios-filled/100/notebook.png" alt="Notebook">
        <h3>{{ notebook.name }}</h3>
        <a href="{{ notebook.path }}">📖 Read</a> |
        <a href="https://your-jupyterhub.com/hub/user-redirect/notebooks/{{ notebook.path }}">🚀 Launch</a>
    </div>
{% endfor %}
</div>
