from typing import List
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http.response import HttpResponseRedirect
from inventory.forms import IngredientCreateForm, IngredientUpdateForm, MenuItemCreateForm, RecipeRequirementCreateForm, PurchaseCreateForm
from inventory.models import Ingredient, MenuItem, Purchase, RecipeRequirement
from account.models import Account
from django.shortcuts import get_object_or_404, render
from django.views.generic.edit import DeleteView, UpdateView
from django.urls import reverse_lazy

# Create your views here.
def home(request):
    return render(request, "inventory/home.html")

@login_required(login_url='/login/')
def ingredient_list(request):
    context = {}
    user_ingredient_list = Ingredient.objects.filter(user=request.user)
    context['user_ingredient_list'] = user_ingredient_list
    return render(request, 'inventory/inventory.html', context)

@login_required(login_url='/login/')
def ingredient_create(request):
    context = {}
    form = IngredientCreateForm(request.POST)

    if form.is_valid():
        ingredient = form.save(commit=False)
        ingredient.user = request.user
        ingredient.expense = ingredient.quantity * ingredient.unit_price
        ingredient.save()
        account = Account.objects.get(username=request.user)
        account.total_expenses += ingredient.expense
        account.save()
        return HttpResponseRedirect('/ingredient/list')

    context['form'] = form
    return render(request, 'inventory/ingredient_create_form.html', context)

@login_required(login_url='/login/')
def ingredient_update(request, id):
    context = {}
    obj = get_object_or_404(Ingredient, id=id)
    form = IngredientUpdateForm(request.POST, instance=obj)

    if form.is_valid():
        form.save()
        item = Ingredient.objects.get(id=id)
        if item.quantity > item.previous_quantity:
            quantity_difference = item.quantity - item.previous_quantity
            new_expense = quantity_difference * item.unit_price
            item.expense += new_expense
            item.save()
            account = Account.objects.get(username=request.user)
            account.total_expenses += new_expense
            account.save()
        item.previous_quantity = item.quantity
        item.save()
        return HttpResponseRedirect('/ingredient/list')

    context['form'] = form

    return render(request, 'inventory/ingredient_update_form.html', context)

class IngredientDelete(LoginRequiredMixin, DeleteView):
    login_url = '/login/'
    model = Ingredient
    template_name = "inventory/ingredient_delete_form.html"
    success_url = reverse_lazy("ingredientlist")

@login_required(login_url='/login/')
def menu_item_list(request):
    context = {}
    user_menu_item_list = MenuItem.objects.filter(user=request.user)
    context['user_menu_item_list'] = user_menu_item_list
    return render(request, 'inventory/menu.html', context)

@login_required(login_url='/login/')
def menu_item_create(request):
    context = {}
    form = MenuItemCreateForm(request.POST)

    if form.is_valid():
        menu_item = form.save(commit=False)
        menu_item.user = request.user
        menu_item.save()
        return HttpResponseRedirect('/menuitem/list')

    context['form'] = form
    return render(request, 'inventory/menu_item_create_form.html', context)

@login_required(login_url='/login/')
def recipe_requirement_create(request, id):
    context = {}
    menu_item = MenuItem.objects.get(id=id)
    recipe_ingredients = RecipeRequirement.objects.filter(menu_item=menu_item)
    form = RecipeRequirementCreateForm(request.POST)
    form.fields['ingredient'].queryset = Ingredient.objects.filter(user=request.user)

    if form.is_valid():
        recipe = form.save(commit=False)
        recipe.menu_item = menu_item
        recipe.save()
    context['form'] = form
    context['menu_item'] = menu_item
    context['recipe_ingredients'] = recipe_ingredients
    return render(request, "inventory/recipe_requirement_create_form.html", context)

@login_required(login_url='/login/')
def recipe_requirement_delete(request, id):
    context = {}
    obj = get_object_or_404(RecipeRequirement, id=id)
    menu_item_id = obj.menu_item.id
    if request.method == "POST":
        obj.delete()
        return HttpResponseRedirect("/reciperequirement/create/{}".format(menu_item_id))
    context["ingredient"] = obj
    context["menu_item_id"] = menu_item_id
    return render(request, "inventory/recipe_requirement_delete_form.html", context)

@login_required(login_url='/login/')
def purchase_list(request):
    context = {}
    user_purchase_list = Purchase.objects.filter(user=request.user)
    context['user_purchase_list'] = user_purchase_list
    return render(request, 'inventory/purchases.html', context)

@login_required(login_url='/login/')
def purchase_create(request):
    context = {}
    form = PurchaseCreateForm(request.POST)
    form.fields['menu_item'].queryset = MenuItem.objects.filter(user=request.user)

    if form.is_valid():
        purchase = form.save(commit=False)
        purchase.user = request.user
        account = Account.objects.get(username=purchase.user)
        item = MenuItem.objects.get(pk=purchase.menu_item.id)
        account.total_revenue += item.price
        account.save()
        purchase.save()
        return HttpResponseRedirect("/purchase/list")
        
    context['form'] = form
    return render(request, "inventory/purchase_create_form.html", context)

@login_required(login_url='/login/')
def profit_report(request):
    account = Account.objects.get(username=request.user)

    total_revenue = account.total_revenue
    total_expenses = account.total_expenses

    total_profit = total_revenue - total_expenses
    total_positive = total_revenue - total_expenses
    if total_positive < 0:
        total_positive *= -1

    context = {
        "total_revenue": total_revenue,
        "total_expenses": total_expenses,
        "total_positive": total_positive,
        "total_profit": total_profit
    }
    return render(request, "inventory/report.html", context)

