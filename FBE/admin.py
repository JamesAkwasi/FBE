
class VoteInline(admin.TabularInline):
    model = Vote
    extra = 0
    readonly_fields = ('phone_number', 'transaction_id', 'created_at')
    can_delete = False

@admin.register(Candidate)
class CandidateAdmin(admin.ModelAdmin):
    list_display = ('name', 'vote_count', 'total_revenue')
    list_filter = ('categories',)
    search_fields = ('name',)
    filter_horizontal = ('categories',)
    inlines = [VoteInline]
    
    def vote_count(self, obj):
        return obj.total_votes()
    vote_count.short_description = 'Votes'
    
    def total_revenue(self, obj):
        return f"{obj.total_revenue():.2f} GHS"
    total_revenue.short_description = 'Revenue'

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'candidate_count')
    search_fields = ('name',)
    
    def candidate_count(self, obj):
        return obj.candidate_set.count()
    candidate_count.short_description = 'Candidates'

@admin.register(Vote)
class VoteAdmin(admin.ModelAdmin):
    list_display = ('candidate', 'phone_number', 'created_at')
    list_filter = ('candidate', 'created_at')
    search_fields = ('phone_number', 'transaction_id')
    readonly_fields = ('created_at',)


    