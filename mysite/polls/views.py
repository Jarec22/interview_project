from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
import requests

from django.utils import timezone

from django.views import generic
from django.views.decorators.cache import cache_page

from .models import Question, Choice
from django.db.models import F

from collections import defaultdict

class IndexView(generic.ListView):
    model = Question
    template_name = 'polls/index.html'
    context_object_name = 'questions'
    paginate_by = 10
    queryset = Question.objects.all().order_by("pub_date")

class DetailView(generic.DetailView):
    model = Question
    template_name = 'polls/detail.html'

    def get_queryset(self):
        return Question.objects.filter(pub_date__lte=timezone.now())


"""
class ResultsView(generic.DetailView):
    model = Question
    template_name = 'polls/results.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        choices = self.object.choice_set.values_list("choice_text", "votes")
        choices_text = [choice[0] for choice in choices]
        choices_votes = [choice[1] for choice in choices]
        context['choices_text'] = choices_text
        context['choices_votes'] = choices_votes
        return context

"""

class ResultsView(generic.DetailView):
    model = Question
    template_name = 'polls/results.html'

    def get_context_data(self, **kwargs):
        pk = self.kwargs['pk']
        question_text = kwargs['object']
        url = "http://127.0.0.1:8080/api/question/{pk}/".format(pk=pk)
        response = requests.get(url)
        choices = response.json()
        choices_text = [choice["choice_text"] for choice in choices]
        choices_votes = [choice["votes"] for choice in choices]
        context = {"choices_text": choices_text,
                "choices_votes": choices_votes,
                "question": {"id":pk,
                            "question_text": question_text}}
        return context      

def vote(request, question_id):
    url = "http://127.0.0.1:8080/api/question/{pk}/vote/{choice}/".format(pk=question_id, choice=request.POST['choice'])
    response = requests.post(url)
    return HttpResponseRedirect(reverse('polls:results', args=(question_id,)))

"""
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
"""


@cache_page(60 * 30)
def summarize(request):
        choices = Choice.objects.values("question", "votes")
        question = None
        tally = defaultdict(int)
        for choice in choices:
            if question != choice["question"]:
                question = choice["question"]
                index = 0
            tally[index] += choice["votes"]
            index += 1
        total_votes = sum(tally.values())
        tally_percentages = [tally_vote / total_votes *100 for tally_vote in tally.values()]
        tally_names = ["A","B","C","D"]
        context = {"tally_percentages": tally_percentages,  "tally_names": tally_names }
        return render(request, 'polls/summary.html', context)