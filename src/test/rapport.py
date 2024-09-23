import dash
from dash import dcc, html, Input, Output
import plotly.graph_objects as go
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import base64

# Initialiser l'application Dash
app = dash.Dash(__name__)

# Exemple de données de graphique
data = {
    'Age Group': ['0-14 ans', '15-24 ans', '25-64 ans', '65 ans et plus'],
    'Hommes': [44886, 43506, 50460, 42794],
    'Femmes': [50670, 46788, 47270, 50402]
}

# Créer un graphique Plotly
fig = go.Figure()
fig.add_trace(go.Bar(x=data['Age Group'], y=data['Hommes'], name='Hommes', marker_color='blue'))
fig.add_trace(go.Bar(x=data['Age Group'], y=data['Femmes'], name='Femmes', marker_color='pink'))

# Disposition de l'application
app.layout = html.Div([
    dcc.Graph(id='population-graph', figure=fig),
    html.Button('Générer le rapport PDF', id='generate-pdf-button'),
    html.Div(id='report-status'),
    dcc.Download(id="download-pdf")
])

# Callback pour générer le PDF
@app.callback(
    Output('download-pdf', 'data'),
    [Input('generate-pdf-button', 'n_clicks')]
)
def generate_pdf(n_clicks):
    if n_clicks is None:
        return dash.no_update

    # Sauvegarder le graphique en tant qu'image PNG
    image_path = "graph.png"
    fig.write_image(image_path)

    # Chemin du fichier PDF de sortie
    pdf_file = "report.pdf"

    # Créer le PDF avec ReportLab
    c = canvas.Canvas(pdf_file, pagesize=letter)
    width, height = letter

    # Ajouter des titres et le graphique au PDF
    c.drawString(100, height - 100, "Rapport de Densité de Population")
    c.drawString(100, height - 120, "Distribution de la population masculine et féminine par tranche d'âge")
    c.drawImage(image_path, 100, height - 500, width=400, height=300)

    # Sauvegarder le fichier PDF
    c.save()

    # Lire le fichier PDF pour le téléchargement
    with open(pdf_file, "rb") as f:
        pdf_data = f.read()

    # Retourner le fichier pour le téléchargement
    return dcc.send_bytes(pdf_data, "report.pdf")

# Lancer l'application
if __name__ == '__main__':
    app.run_server(debug=True)
