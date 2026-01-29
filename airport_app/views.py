from django.shortcuts import render, redirect
from django.contrib import messages
from .models import AirportRoute
from .forms import AirportRouteForm, SearchLastReachableForm


def add_route(request):
    # create a new airport route node.
    
    form = AirportRouteForm(request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            route = form.save()
            messages.success(
                request,
                f"Airport node '{route.airport_code}' created successfully!"
            )
            return redirect('add_route')
        else:
            messages.error(
                request,
                "Please correct the errors below."
            )

    # Get all nodes for display
    nodes = AirportRoute.objects.select_related('parent').all()
    
    # Get root nodes for tree visualization
    root_nodes = AirportRoute.objects.filter(parent=None)

    context = {
        'form': form,
        'nodes': nodes,
        'root_nodes': root_nodes,
    }
    
    return render(request, 'flight_routes/add_route.html', context)


def find_last_reachable(request):
    """
    Question 1: Find the Last Reachable Node in an Airport Route.
    
    User selects a starting node and direction (Left/Right).
    The system should traverse through the connected airport nodes continuously in the
    selected direction and display the last reachable airport node.
    """
    form = SearchLastReachableForm(request.POST or None)
    result = None

    if request.method == 'POST':
        if form.is_valid():
            start_node = form.cleaned_data['start_node']
            direction = form.cleaned_data['direction']
            
            # Find the last reachable node
            result = start_node.find_last_reachable(direction)
            
            if result == start_node:
                messages.info(
                    request,
                    f"No {direction} children exist. The starting node itself is the last reachable."
                )
            else:
                messages.success(
                    request,
                    f"Last reachable node found in {direction} direction!"
                )

    context = {
        'form': form,
        'result': result,
    }
    
    return render(request, 'flight_routes/find_last_reachable.html', context)


def longest_duration(request):
    """
    Question 2: Find the Airport with the Longest Duration.
    
    Display the airport node that has the highest duration value.
    """
    node = AirportRoute.get_longest_duration_node()
    
    context = {
        'node': node,
    }
    
    return render(request, 'flight_routes/longest_duration.html', context)


def shortest_duration(request):
    """
    Question 3: Find the Airport with the Shortest Duration Across the Entire Airport Route.
    
    Display the airport node with the minimum duration value across all nodes.
    """
    node = AirportRoute.get_shortest_duration_node()
    
    context = {
        'node': node,
    }
    
    return render(request, 'flight_routes/shortest_duration.html', context)


def dashboard(request):
    """
    Dashboard view showing statistics and overview.
    """
    total_nodes = AirportRoute.objects.count()
    root_nodes = AirportRoute.objects.filter(parent=None)
    longest = AirportRoute.get_longest_duration_node()
    shortest = AirportRoute.get_shortest_duration_node()
    
    # Calculate total duration
    total_duration = sum(node.duration for node in AirportRoute.objects.all())
    
    context = {
        'total_nodes': total_nodes,
        'root_nodes': root_nodes,
        'longest': longest,
        'shortest': shortest,
        'total_duration': total_duration,
    }
    
    return render(request, 'flight_routes/dashboard.html', context)