from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.views import generic
from django.db.models import F
from django.utils import timezone
from collections import defaultdict
from django.views.decorators.cache import cache_page

from .models import Question, Choice

class IndexView(generic.ListView):
    model = Question
    template_name = 'polls/index.html'
    context_object_name = 'questions'
    paginate_by = 10
    queryset = Question.objects.all()


    #def get_queryset(self):
        #return Question.objects.filter(pub_date__lte=timezone.now()).order_by('-pub_date')[:10]
        #return Question.objects.all()

class DetailView(generic.DetailView):
    model = Question
    template_name = 'polls/detail.html'

    def get_queryset(self):
        return Question.objects.filter(pub_date__lte=timezone.now())

class ResultsView(generic.DetailView):
    model = Question
    template_name = 'polls/results.html'

    def get_context_data(self, *args, **kwargs):
        self.object = self.get_object()
        context = super(ResultsView, self).get_context_data(**kwargs)
        question = Question.objects.get(pk=self.kwargs['pk'])
        choices = question.choice_set.all()
        choices_text = [choice.choice_text for choice in choices]
        choices_votes = [choice.votes for choice in choices]
        context['choices_text'] = choices_text
        context['choices_votes'] = choices_votes
        return context

def vote(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    try:
        selected_choice = question.choice_set.get(pk=request.POST['choice'])
    except (KeyError, Choice.DoesNotExist):
        return render(request, 'polls/detail.html', 
        {
            'question': question,
            'error_message': "You didn't select a choice.",
        })
    else:
        selected_choice.votes = F('votes') + 1
        selected_choice.save()
        return HttpResponseRedirect(reverse('polls:results', args=(question.id,)))

@cache_page(60 * 30)
def summarize(request):
        choices = Choice.objects.values("question", "votes")
        question = 0
        tally = defaultdict(int)
        for choice in choices:
            if question == choice["question"]:
                index += 1
                tally[index] += choice["votes"]
            else:
                index = 0
                question = choice["question"]
                tally[index] += choice["votes"]
            tally_percentages = [tally_vote/sum(tally.values())*100 for tally_vote in tally.values()]
        context = {"tally_percentages": tally_percentages, "tally_names":["A","B","C","D"] }
        return render(request, 'polls/summary.html', context)