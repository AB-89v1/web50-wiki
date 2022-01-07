import markdown2
import random
from django.shortcuts import render
from django import forms
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse

from . import util
from markdown2 import Markdown

class SearchForm(forms.Form):
    query = forms.CharField(label="Search Encyclopedia")

class NewPageForm(forms.Form):
    title = forms.CharField(label="Entry Title:")
    content = forms.CharField(
        widget=forms.Textarea(),
        label="Entry Content:")
        
class EditPageForm(forms.Form):
    content = forms.CharField(
        widget=forms.Textarea(),
        label="Edit Content:")
    entryTitle = forms.CharField(
        widget=forms.HiddenInput())

def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries(),
        "searchform": SearchForm
    })

#Borrowed from GitHub user EgidioHPaixao
def entry(request, entry):
    markdowner = Markdown()
    entryPage = util.get_entry(entry)
    if entryPage is None:
        return render(request, "encyclopedia/notfound.html", {
            "entryTitle": entry
                      })
    else:
        return render(request, "encyclopedia/entry.html", {
            "entry": markdowner.convert(entryPage),
            "entryTitle": entry
        })

def search(request):
    #check if request is post
    if request.method == "POST":
        
        #Take in form data
        form = SearchForm(request.POST)
        
        #server-side form validation
        if form.is_valid():
        
            #Isolate search query
            query = form.cleaned_data["query"]
        
            #Look for entry matching that term
            entryPage = util.get_entry(query)
        
            if entryPage is None:
                    #No match found, check as substring:
                    
                    #declare list of search results
                    results = []
                    
                    #get list of all encyclopedia entries
                    entries = util.list_entries()
                    
                    #loop through entry names, checking for query as substring and adding if match
                    for entry in entries:
                        if f"{query}" in entry:
                            results.append(entry)
                    
                    #If partial matches not found, return 'not found' template
                    if not results:
                        return render(request, "encyclopedia/notfound.html", {
                            "entryTitle": query
                        })
                    #If at least one match found, return index page
                    else:
                        return render(request, "encyclopedia/searchresults.html", {
                            "entries": results,
                            "query": query
                        })
                        
                            
            else:
                markdowner = Markdown()
                return render(request, "encyclopedia/entry.html", {
                        "entry": markdowner.convert(entryPage),
                        "entryTitle": query
                })
def new_page(request):
    if request.method == "POST":
        #take in form data
        form = NewPageForm(request.POST)
        
        #validate
        if form.is_valid():
        
            #isolate inputs
            title = form.cleaned_data["title"]
            content = form.cleaned_data["content"]
            
            #Check if entry with matching title already exists
            if util.get_entry(title) is None:
            
                #Save new entry, send user to page
                util.save_entry(title, content)
                return HttpResponseRedirect(reverse('entry', kwargs={'entry': title}))
                
            else:
                return render(request, "encyclopedia/newerror.html", {
                    "title": title
                              })
            
    else:
        return render(request, "encyclopedia/new.html", {
            "addform": NewPageForm
                      })

def edit(request):
    if request.method == "POST":
        #Check for title
        if request.POST.get('title'):
            title = request.POST.get('title')
            content = util.get_entry(title)
            form = EditPageForm(initial={"content": content, "entryTitle": title})
            return render(request, "encyclopedia/edit.html", {
            "editform": form,
            "entryTitle": title
            })
        else:
            form = EditPageForm(request.POST)
            if form.is_valid():
                content = form.cleaned_data["content"]
                title = form.cleaned_data["entryTitle"]
                util.save_entry(title, content)
                return HttpResponseRedirect(reverse('entry', kwargs={'entry': title}))
            else:
                return HttpResponse("Form wasn't valid")
    else:
        return HttpResponse("Request wasn't POST")

def random_(request):
    list = util.list_entries()
    length = len(list)
    index = random.randint(0,(length-1))
    entry = list[index]
    return HttpResponseRedirect(reverse('entry', kwargs={'entry': entry}))
