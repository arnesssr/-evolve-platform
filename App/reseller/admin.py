"""Admin configuration for reseller models."""
from django.contrib import admin
from django.utils.html import format_html
from .earnings.models import Reseller, Commission, Invoice, Payout


@admin.register(Reseller)
class ResellerAdmin(admin.ModelAdmin):
    list_display = ['user', 'company_name', 'tier', 'commission_rate', 'total_sales', 'is_active', 'created_at']
    list_filter = ['tier', 'is_active', 'is_verified', 'created_at']
    search_fields = ['user__username', 'user__email', 'company_name', 'referral_code']
    readonly_fields = ['referral_code', 'total_sales', 'total_commission_earned', 'total_commission_paid', 
                      'pending_commission', 'created_at', 'modified_at']
    
    fieldsets = (
        ('User Information', {
            'fields': ('user', 'referral_code')
        }),
        ('Company Details', {
            'fields': ('company_name', 'company_website', 'company_description')
        }),
        ('Contact Information', {
            'fields': ('phone_number', 'alternate_email', 'address', 'city', 'state', 'country', 'postal_code')
        }),
        ('Reseller Status', {
            'fields': ('tier', 'commission_rate', 'is_active', 'is_verified', 'verified_at')
        }),
        ('Financial Information', {
            'fields': ('payment_method', 'bank_account_name', 'bank_account_number', 'bank_name', 
                      'bank_routing_number', 'paypal_email')
        }),
        ('Metrics', {
            'fields': ('total_sales', 'total_commission_earned', 'total_commission_paid', 'pending_commission')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'modified_at')
        })
    )


@admin.register(Commission)
class CommissionAdmin(admin.ModelAdmin):
    list_display = ['transaction_reference', 'reseller', 'client_name', 'sale_amount', 'amount', 
                   'commission_rate', 'status', 'calculation_date']
    list_filter = ['status', 'calculation_date', 'reseller__tier']
    search_fields = ['transaction_reference', 'client_name', 'client_email', 'product_name']
    readonly_fields = ['calculation_date', 'created_at', 'modified_at']
    date_hierarchy = 'calculation_date'
    
    fieldsets = (
        ('Commission Details', {
            'fields': ('reseller', 'transaction_reference', 'status')
        }),
        ('Transaction Information', {
            'fields': ('client_name', 'client_email', 'product_name', 'product_type')
        }),
        ('Financial Details', {
            'fields': ('sale_amount', 'commission_rate', 'amount', 'tier_bonus')
        }),
        ('Dates', {
            'fields': ('calculation_date', 'approval_date', 'paid_date')
        }),
        ('Related Records', {
            'fields': ('invoice', 'payout', 'notes')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'modified_at')
        })
    )
    
    actions = ['approve_commissions', 'reject_commissions']
    
    def approve_commissions(self, request, queryset):
        count = queryset.filter(status='pending').update(status='approved')
        self.message_user(request, f'{count} commissions approved.')
    approve_commissions.short_description = 'Approve selected commissions'
    
    def reject_commissions(self, request, queryset):
        count = queryset.filter(status='pending').update(status='rejected')
        self.message_user(request, f'{count} commissions rejected.')
    reject_commissions.short_description = 'Reject selected commissions'


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ['invoice_number', 'reseller', 'period_display', 'total_amount', 'status_badge', 
                   'issue_date', 'due_date']
    list_filter = ['status', 'issue_date', 'due_date']
    search_fields = ['invoice_number', 'reseller__user__username', 'reseller__company_name']
    readonly_fields = ['invoice_number', 'created_at', 'modified_at']
    date_hierarchy = 'issue_date'
    
    fieldsets = (
        ('Invoice Information', {
            'fields': ('reseller', 'invoice_number', 'status')
        }),
        ('Period', {
            'fields': ('period_start', 'period_end', 'description')
        }),
        ('Financial Details', {
            'fields': ('subtotal', 'tax_amount', 'total_amount')
        }),
        ('Dates', {
            'fields': ('issue_date', 'due_date', 'payment_date')
        }),
        ('Additional Information', {
            'fields': ('pdf_file', 'line_items', 'notes')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'modified_at')
        })
    )
    
    def period_display(self, obj):
        return f"{obj.period_start} to {obj.period_end}"
    period_display.short_description = 'Period'
    
    def status_badge(self, obj):
        color = obj.get_status_color()
        return format_html(
            '<span style="color: white; background-color: {}; padding: 3px 10px; border-radius: 3px;">{}</span>',
            color, obj.get_status_display()
        )
    status_badge.short_description = 'Status'


@admin.register(Payout)
class PayoutAdmin(admin.ModelAdmin):
    list_display = ['reference_number', 'reseller', 'amount', 'payment_method', 'status_badge', 
                   'request_date', 'completion_date']
    list_filter = ['status', 'payment_method', 'request_date']
    search_fields = ['reference_number', 'reseller__user__username', 'reseller__company_name', 
                    'transaction_reference']
    readonly_fields = ['reference_number', 'net_amount', 'created_at', 'modified_at']
    date_hierarchy = 'request_date'
    
    fieldsets = (
        ('Payout Information', {
            'fields': ('reseller', 'reference_number', 'status', 'invoice')
        }),
        ('Payment Details', {
            'fields': ('payment_method', 'payment_details')
        }),
        ('Financial Information', {
            'fields': ('amount', 'transaction_fee', 'net_amount')
        }),
        ('Processing', {
            'fields': ('request_date', 'process_date', 'completion_date', 'approved_by')
        }),
        ('Transaction Details', {
            'fields': ('transaction_reference', 'failure_reason', 'notes')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'modified_at')
        })
    )
    
    actions = ['process_payouts', 'complete_payouts', 'fail_payouts']
    
    def status_badge(self, obj):
        color_map = {
            'requested': '#ffc107',
            'processing': '#17a2b8',
            'completed': '#28a745',
            'failed': '#dc3545',
            'cancelled': '#6c757d',
        }
        color = color_map.get(obj.status, '#6c757d')
        return format_html(
            '<span style="color: white; background-color: {}; padding: 3px 10px; border-radius: 3px;">{}</span>',
            color, obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    
    def process_payouts(self, request, queryset):
        count = 0
        for payout in queryset.filter(status='requested'):
            payout.process_payout()
            count += 1
        self.message_user(request, f'{count} payouts marked as processing.')
    process_payouts.short_description = 'Mark as processing'
    
    def complete_payouts(self, request, queryset):
        count = 0
        for payout in queryset.filter(status='processing'):
            payout.complete_payout()
            count += 1
        self.message_user(request, f'{count} payouts completed.')
    complete_payouts.short_description = 'Mark as completed'
    
    def fail_payouts(self, request, queryset):
        count = queryset.filter(status__in=['requested', 'processing']).update(status='failed')
        self.message_user(request, f'{count} payouts marked as failed.')
    fail_payouts.short_description = 'Mark as failed'
