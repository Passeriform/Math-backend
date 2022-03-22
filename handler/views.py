"""Django app views."""
from django.http import JsonResponse
from django.conf import settings
from django.views.decorators.http import require_http_methods
from sympy import *
from sympy.parsing.sympy_parser import *


def OutputLevelForMaxProfit(cost_str, price_str):
    prelim = list(dict())
    prelim.append({
        "type": "MathMsg",
        "message": f'''"The firm produces at "\
            {latex(Symbol('MC'))}={latex(Symbol('P'))}\
            "to maximize profit."'''})

    prelim.append({
        "type": "MathMsg",
        "message": f'''{latex(Symbol('MC'))}=\
            {latex(Symbol('Marginal Cost'))}\" and \"\
            {latex(Symbol('P'))}={latex(Symbol('Price'))}'''})

    ###########################################################################

    root_output = list(dict())
    root_output.append({
        "type": "MathMsg",
        "message": f'''{latex(Symbol('MC'))}" is the change in total cost or its \
            function. Its found by taking the first order differential."'''})

    transformations = (standard_transformations +
                       (implicit_multiplication_application, convert_xor,))

    cost = parse_expr(cost_str, transformations=transformations)
    price = Float(price_str, precision=5)
    wrt_sym = cost.free_symbols.pop()
    marginal_cost = diff(cost, wrt_sym)

    root_output.append({
        "type": "PureMath",
        "message": f'''{latex(Symbol('MC'))}=\
            {latex(Derivative(Symbol("C"), wrt_sym))}=\
            {latex(Derivative(cost, wrt_sym))}=\
            {latex(marginal_cost)}'''})

    root_output.append({
        "type": "PureMath",
        "message": f'''{latex(Symbol('MC'))}=\
            {latex(marginal_cost)}'''})

    root_output.append({"type": "TipMsg", "message": "Equating to P..."})

    root_output.append({
        "type": "PureMath", "message": f'{latex(marginal_cost)}={latex(price)}'})

    roots = solveset(marginal_cost - price, wrt_sym)

    inflection = list(dict())
    max_p_pt = 0

    for root in roots:
        delta = diff(marginal_cost, wrt_sym).subs(wrt_sym, root).evalf()

        if delta > 0:
            max_p_pt = root if root >= max_p_pt else max_p_pt
            inflection.append({"root": root, "delta": "increasing"})
        else:
            inflection.append({"root": root, "delta": "decreasing"})

    root_output.append({
        "type": "PureMath",
        "message": ' or '.join([f"""{latex(wrt_sym)}=\
            {latex(inflection_pt['root'])}""" for inflection_pt in inflection])})

    ###########################################################################

    root_result = list(dict())
    root_result.append({
        "type": "MathMsg",
        "message": '\" and \"'.join([f'''{latex(wrt_sym)}=\
            {latex(inflection_pt['root'])}", then "\
            {latex(Symbol('MC'))}" is "{inflection_pt['delta']}''' \
            for inflection_pt in inflection])})

    root_result.append({
        "type": "MathMsg",
        "message": f'''"So, the profit it maximum at "\
            {latex(wrt_sym)}={latex(max_p_pt)} units.'''})

    ###########################################################################

    elasticity_output = list(dict())
    elasticity_output.append({
        "type": "TipMsg", "message": "Output elasticity formula is:"})

    formula = Symbol('C')/wrt_sym * Derivative(wrt_sym, Symbol('C'))
    subs_sym = formula.subs(
        Derivative(wrt_sym, Symbol('C')), 1/Derivative(cost, wrt_sym))
    subs_vals = subs_sym.subs(Symbol('C'), cost).subs(Derivative(cost, wrt_sym), marginal_cost)

    result = (cost/(wrt_sym * diff(cost, wrt_sym))).subs(wrt_sym, max_p_pt).evalf()

    elasticity_output.append({"type": "PureMath", "message": latex(formula)})
    elasticity_output.append({"type": "PureMath",
                              "message": f'={latex(subs_sym)}'})
    elasticity_output.append({"type": "PureMath",
                              "message": f'={latex(subs_vals)}'})
    elasticity_output.append({"type": "PureMath", "message": f'={latex(result)}'})

    ###########################################################################

    result_output = list()
    result_output.append({"type": "TipMsg",
                             "message": f'The output elasticity is {result}'})

    ###########################################################################

    step_output = list()
    step_output.append(prelim)
    step_output.append(root_output)
    step_output.append(root_result)
    step_output.append(elasticity_output)
    step_output.append(result_output)

    ###########################################################################

    return step_output


def calculate(request):
    """Return a message object containing output for a problem.

    Args:
        op (str): Operation needed to be performed.
        cost (`expression`): A mathematical expression for cost.
        p (int): Elasticity `p` value.

    Returns:
        Message: Return an array of cards with messages.
    """

    operation = request.GET.get('op', None)

    if operation == "output_level":
        cost = request.GET.get('cost', None)
        p = request.GET.get('p', None)

        result = OutputLevelForMaxProfit(cost, p)

    return JsonResponse({"data": result})
