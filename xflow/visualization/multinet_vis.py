# imports
import dash
import random
from dash import dcc
from dash import html

from dash.dependencies import Input, Output
import plotly.graph_objs as go
import networkx as nx
import ndlib.models.epidemics as ep
from ndlib.models.ModelConfig import Configuration

import pandas as pd
from dash import dash_table

# - - - - - - - - - - - - - - - - - - - - -
# Set the number of simulation time steps
TIME_STEPS = 3
# - - - - - - - - - - - - - - - - - - - - -


def get_sir_model(graph, num_infected, beta, gamma):
    """Returns a configured SIR model for the given graph."""
    model = ep.SIRModel(graph)
    config = Configuration()
    config.add_model_parameter("beta", beta)
    config.add_model_parameter("gamma", gamma)
    infected_nodes = random.sample(list(graph.nodes()), num_infected)
    config.add_model_initial_configuration("Infected", infected_nodes)
    model.set_initial_status(config)
    return model


def run_sir_model(model, time_steps):
    """Runs the given SIR model for the given number of time steps."""
    return model.iteration_bunch(time_steps)

# Create two random graphs with different numbers of nodes
network_layers = [nx.erdos_renyi_graph(9, 0.06), nx.erdos_renyi_graph(11, 0.06)]

# Assign random positions for the nodes in each network layer
for G in network_layers:
    for node in G.nodes():
        G.nodes[node]["pos"] = (random.uniform(-1, 1), random.uniform(-1, 1))

# #Initialize the spin attribute for each node
# for G in network_layers:
#     for node in G.nodes():
#         G.nodes[node]["spin"] = random.choice([0, 1])  # for example, if spin can be -1 or 1
#         G.nodes[node]["pos"] = (random.uniform(-1, 1), random.uniform(-1, 1))


# Get some of the nodes in layer 0
num_nodes_to_connect = int(len(network_layers[0].nodes()) * 0.1)
nodes_layer0_to_connect = random.sample(network_layers[0].nodes(), num_nodes_to_connect)

# Pair each selected node in layer 0 with a node in layer 1
for node0, node1 in zip(nodes_layer0_to_connect, network_layers[1].nodes()):
    network_layers[0].add_edge(node0, node1)
    network_layers[1].add_edge(node0, node1)

# ising
#Check for the 'spin' attribute
# def calculate_energy(graph, J=1, H=0):
#     energy = 0
#     for node in graph.nodes():
#         si = graph.nodes[node].get("spin", 0)  # Use a default value if 'spin' is not present
#         energy -= H * si
#         for neighbor in graph.neighbors(node):
#             sj = graph.nodes[neighbor].get("spin", 0)
#             energy -= J * si * sj
#     print (energy / 2)
#     return energy / 2  # Each pair is counted twice

# Add this function to calculate energy of a given layer at a specific timestep
# def calculate_energy(model_result, layer_index, timestep):
#     status_at_timestep = model_result[layer_index][timestep]["status"]
#     #print(status_at_timestep)
#     energy = sum(1 if status == 1 else 0 for status in status_at_timestep.values())
#     #print (energy)
#     return energy


# Initialize the app
app = dash.Dash(
    __name__,
    external_stylesheets=[
        "https://cdn.jsdelivr.net/npm/bootstrap@4.3.1/dist/css/bootstrap.min.css"
    ],
)

app.layout = html.Div(
    [
        # html.Div([
        #     dcc.Graph(id="energy-plot", style={"height": "400px", "width": "100%"})
        # ], className="col-9"), 

        html.Div([
            dcc.Graph(id="3d-scatter-plot", style={"height": "800px", "width": "100%"}),
        ], className="col-9"),  # This div wraps the scatter plot

        html.Div([
            html.Label("Initial infected nodes:", style={"font-weight": "bold"}),
            html.P("The initial number of infected nodes in the graph."),
            dcc.Input(id="input-infected", type="number", value=1),
            html.Label("Beta (Infection rate):", style={"font-weight": "bold"}),
            html.P(
                "The probability of disease transmission from an infected node to a susceptible node."
            ),
            dcc.Slider(id="beta-slider", min=0, max=1, step=0.1, value=0.8),
            html.Label("Gamma (Recovery rate):", style={"font-weight": "bold"}),
            html.P(
                "The probability of an infected node moving into the recovered stage in each time step."
            ),
            dcc.Slider(id="gamma-slider", min=0, max=1, step=0.1, value=0.01),
            html.Label("Time:", style={"font-weight": "bold"}),
            html.P("The time step at which to view the state of the graph."),
            dcc.Slider(
                id="time-slider",
                min=0,
                max=TIME_STEPS - 1,
                value=0,
                marks={str(i): f"{i}" for i in range(TIME_STEPS)},
                step=None,
            ),
            dash_table.DataTable(id="status-table"),
        ], className="col-3"),  # This div wraps the controls
    ],
    className="row"  # Bootstrap's row class to contain both of the above divs
)

@app.callback(
    Output("status-table", "data"),
    Output("status-table", "columns"),
    [
        Input("time-slider", "value"),
        Input("input-infected", "value"),
        Input("beta-slider", "value"),
        Input("gamma-slider", "value"),
    ],
)

def update_table(time_step, num_infected, beta, gamma):
    for layer in network_layers:
        print("layer", layer)

    models = [
        get_sir_model(layer, num_infected, beta, gamma) for layer in network_layers
    ]

    # for model in models:
    #     print("model", model)

    model_results = [run_sir_model(model, TIME_STEPS) for model in models]
    # print("model_results", model_results)


    # Compute the counts of each status at the current time step
    # status_counts = {"Susceptible": 0, "Infected": 0, "Recovered": 0}
    # for result in model_results:
    #     for status, count in result[time_step]["node_count"].items():
    #         if status == 0:
    #             status_counts["Susceptible"] += count
    #         elif status == 1:
    #             status_counts["Infected"] += count
    #         elif status == 2:
    #             status_counts["Recovered"] += count

    # # Initialize status count dictionaries for each layer
    status_counts_total = {"Susceptible": 0, "Infected": 0, "Recovered": 0}
    status_counts_layer0 = {"Susceptible": 0, "Infected": 0, "Recovered": 0}
    status_counts_layer1 = {"Susceptible": 0, "Infected": 0, "Recovered": 0}

    # Compute the counts of each status at the current time step for each layer
    for layer_index, result in enumerate(model_results):
        for status, count in result[time_step]["node_count"].items():
            if status == 0:
                status_counts_total["Susceptible"] += count
                # print("layer_index", layer_index)
                if layer_index == 0:
                    status_counts_layer0["Susceptible"] += count
                elif layer_index == 1:
                    status_counts_layer1["Susceptible"] += count
            elif status == 1:
                status_counts_total["Infected"] += count
                if layer_index == 0:
                    status_counts_layer0["Infected"] += count
                elif layer_index == 1:
                    status_counts_layer1["Infected"] += count
            elif status == 2:
                status_counts_total["Recovered"] += count
                if layer_index == 0:
                    status_counts_layer0["Recovered"] += count
                elif layer_index == 1:
                    status_counts_layer1["Recovered"] += count


    print('model_results', model_results)
    for layer_index, result in enumerate(model_results):
        print('layer_index', layer_index)
        print('result', result)
        for status, count in result[time_step]["node_count"].items():
            print('status', status)

        # Iterating over the list of result dictionaries
    for layer_index, result_dict in enumerate(model_results):
        print('layer_index', layer_index)
        
        # Iterating over the dictionaries in the result list
        for single_result in result_dict:
            # Extracting the 'iteration' value
            iteration = single_result.get('iteration')
            print('iteration', iteration)
            
            # Extracting the 'status' value
            status = single_result.get('status')
            print('status', status)


    # # Initialize the neighbor_energy counter
    # neighbor_energy = 0

    # # Assuming layer0 is the graph representing layer 0
    # layer0 = network_layers[0]  # replace with the actual graph object if different

    # # print('layer0', layer0)
    # # print('layer0.nodes', layer0.nodes())

    # # Iterate through each node in layer0
    # for node in layer0.nodes():
    #     print('node in layer0', node)
    #     # Get the status of the current node
    #     node_status = layer0.nodes[node].get("status")  # assuming status is stored with the key "status"
    #     print('node_status', node_status)
    #     # Check the status of each neighbor
    #     for neighbor in layer0.neighbors(node):
    #         neighbor_status = layer0.nodes[neighbor].get("status", -1)
            
    #         # Check if either the node or the neighbor is infected
    #         if node_status == 1 or neighbor_status == 1:
    #             # If either node is infected and the other is not,
    #             # increment the neighbor_energy counter
    #             if node_status != neighbor_status:
    #                 neighbor_energy += 1

    # # At this point, neighbor_energy holds the total neighbor energy for the entire layer 0
    # print("Neighbor Energy for Layer 0:", neighbor_energy)


    

    # Create a DataFrame and format it for use with DataTable
    df = pd.DataFrame([status_counts_total])
    data = df.to_dict("records")
    columns = [{"name": i, "id": i} for i in df.columns]

    print("Step", time_step)
    # print("Susceptible", status_counts["Susceptible"])
    # print("Infected", status_counts["Infected"])
    # print("Recovered", status_counts["Recovered"])

    print("Susceptible status_counts_total", status_counts_total["Susceptible"])
    print("Infected status_counts_total", status_counts_total["Infected"])
    print("Recovered status_counts_total", status_counts_total["Recovered"])

    print("Susceptible status_counts_layer0", status_counts_layer0["Susceptible"])
    print("Infected status_counts_layer0", status_counts_layer0["Infected"])
    print("Recovered status_counts_layer0", status_counts_layer0["Recovered"])

    print("Susceptible status_counts_layer1", status_counts_layer1["Susceptible"])
    print("Infected status_counts_layer1", status_counts_layer1["Infected"])
    print("Recovered status_counts_layer1", status_counts_layer1["Recovered"])

    # Calculate the energy for layer 0
    high_energy_layer0 = status_counts_layer0["Infected"]
    print ("high_energy_layer0", high_energy_layer0)

    low_energy_layer0 = status_counts_layer0["Susceptible"] + status_counts_layer0["Recovered"]
    print ("low_energy_layer0", low_energy_layer0)
   
    # Calculate the energy for layer 1
    high_energy_layer1 = status_counts_layer1["Infected"]
    print ("high_energy_layer1", high_energy_layer1)

    low_energy_layer1 = status_counts_layer1["Susceptible"] + status_counts_layer1["Recovered"]
    print ("low_energy_layer1", low_energy_layer1)

    # # For Layer 0
    # current_states_layer0 = model_results[0][time_step]["node_states"]
    # graph0 = nx.Graph()
    # for node, state in current_states_layer0.items():
    #     graph0.add_node(node, state=state)
    
    # # For Layer 1
    # current_states_layer1 = model_results[1][time_step]["node_states"]
    # graph1 = nx.Graph()
    # for node, state in current_states_layer1.items():
    #     graph1.add_node(node, state=state)

    # Calculate criteria_two
    # criteria_two_result = criteria_two(graph0, graph1)

    # # Print or return the criteria_two_result as needed
    # print("Criteria Two Result:", criteria_two_result)

    return data, columns

# @app.callback(
#     Output("energy-plot", "figure"),
#     [
#         Input("time-slider", "value"),
#         Input("input-infected", "value"),
#         Input("beta-slider", "value"),
#         Input("gamma-slider", "value"),
#     ],
# )

# def update_energy_plot(time_step, num_infected, beta, gamma):
#     # Run the SIR model with the provided parameters
#     models = [get_sir_model(layer, num_infected, beta, gamma) for layer in network_layers]
#     model_results = [run_sir_model(model, TIME_STEPS) for model in models]
    
#     # Update the state of nodes based on the model results for the current time step
#     # ... (code for updating node states, if needed)

#     energies = []
#     for step in range(TIME_STEPS):
#         # Calculate the energy of the system at this step
#         energy = sum(calculate_energy(layer) for layer in network_layers)
#         energies.append(energy)

#     # Create the energy plot
#     energy_trace = go.Scatter(x=list(range(TIME_STEPS)), y=energies, mode='lines', name='Energy')
#     layout = go.Layout(title='Energy of the System', xaxis=dict(title='Time Step'), yaxis=dict(title='Energy'))
    
#     return {"data": [energy_trace], "layout": layout}


@app.callback(
    Output("3d-scatter-plot", "figure"),
    [
        Input("time-slider", "value"),
        Input("input-infected", "value"),
        Input("beta-slider", "value"),
        Input("gamma-slider", "value"),
    ],
)
def update_graph(time_step, num_infected, beta, gamma):
    models = [
        get_sir_model(layer, num_infected, beta, gamma) for layer in network_layers
    ]
    model_results = [run_sir_model(model, TIME_STEPS) for model in models]

    data = []

    # Create traces for edges and nodes
    for idx, network in enumerate(network_layers):
        edge_trace = go.Scatter3d(
            x=[],
            y=[],
            z=[],
            line={"width": 0.5, "color": "#888"},
            hoverinfo="none",
            mode="lines",
        )

        node_trace = go.Scatter3d(
            x=[],
            y=[],
            z=[],
            mode="markers",
            hoverinfo="text",
            marker={
                "showscale": False,
                "colorscale": "Viridis",
                "reversescale": True,
                "color": [],
                "size": 6,
                "opacity": 0.8,
                "line": {"width": 0.5, "color": "#888"},
            },
        )

        # Add edges to trace
        for edge in network.edges():
            x0, y0 = network.nodes[edge[0]]["pos"]
            x1, y1 = network.nodes[edge[1]]["pos"]
            edge_trace["x"] += (x0, x1, None)
            edge_trace["y"] += (y0, y1, None)
            edge_trace["z"] += (idx, idx, None)

        # Add nodes to trace
        for node in network.nodes:
            x, y = network.nodes[node]["pos"]
            node_trace["x"] += (x,)
            node_trace["y"] += (y,)
            node_trace["z"] += (idx,)
            status = 0
            if node in model_results[idx][time_step]["status"]:
                status = model_results[idx][time_step]["status"][node]
            color = (
                "red" if status == 1 else "green" if status == 2 else "grey"
            )  # Color based on the infection status
            node_trace["marker"]["color"] += (color,)

        data.extend((edge_trace, node_trace))

    # Add inter-layer edges to trace
    inter_edge_trace = go.Scatter3d(
        x=[],
        y=[],
        z=[],
        line=dict(width=2, color=[]),  # Set color dynamically
        hoverinfo="none",
        mode="lines",
    )

    # Initialize a list to store the color of each link
    inter_edge_colors = []

    # Add inter-layer edges to trace
    for index, (node0, node1) in enumerate(zip(network_layers[0].nodes(), network_layers[1].nodes())):
        x0, y0 = network_layers[0].nodes[node0]["pos"]
        x1, y1 = network_layers[1].nodes[node1]["pos"]
        inter_edge_trace["x"] += (x0, x1, None)
        inter_edge_trace["y"] += (y0, y1, None)
        inter_edge_trace["z"] += (0, 1, None)
        
        # Color the selected link red, and others light yellow
        link_color = "red" if index == 0 else "blue"  # Change index as needed
        inter_edge_colors.append(link_color)

    # Assign the list of colors to the 'color' attribute of 'line' dictionary
    inter_edge_trace["line"]["color"] = inter_edge_colors

    data.append(inter_edge_trace)

    # Define layout
    layout = go.Layout(
        scene=dict(
            xaxis=dict(title="", showticklabels=False, range=[-1, 1], autorange=False),
            yaxis=dict(title="", showticklabels=False, range=[-1, 1], autorange=False),
            zaxis=dict(title="", showticklabels=False, range=[-1, 1], autorange=False),
            aspectratio=dict(x=1, y=1, z=1),
            camera=dict(eye=dict(x=1.2, y=1.2, z=1.2)),
        )
    )

    return {"data": data, "layout": layout}


if __name__ == "__main__":
    app.run_server(debug=True)
