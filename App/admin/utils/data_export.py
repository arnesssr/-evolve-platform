# CSV export helpers for admin module
from typing import Iterable, Dict
from django.http import HttpResponse


def export_resellers_to_csv(rows: Iterable[Dict]) -> HttpResponse:
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="resellers.csv"'
    header = ['id','name','email','company','commission_tier','total_earnings','sales_count','status','joined']
    response.write(','.join(header) + '\n')
    for r in rows:
        line = [
            str(r.get('id','')),
            str(r.get('name','')),
            str(r.get('email','')),
            str(r.get('company','')),
            str(r.get('commission_tier','')),
            str(r.get('total_earnings','')),
            str(r.get('sales_count','')),
            str(r.get('status','')),
            str(r.get('joined','')),
        ]
        response.write(','.join(line) + '\n')
    return response

