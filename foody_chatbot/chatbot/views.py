from django.shortcuts import get_object_or_404, render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import permissions
# Create your views here.
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.urls import reverse
from rest_framework import authentication, permissions
from .models import Choice, Question
from .utils.dialog_utils import remove_payload
from .utils.foody_utils import FoodySearch 
# from openai_utils import ChatGPT
import json
import openai
import os
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv('API_KEY')

foody_search = FoodySearch()

def ChatGPT(dialog, temperature=0.7, max_tokens=2048, model='gpt-3.5-turbo', functions = None, keep_response = False):
    assert isinstance(dialog, list)
    response = openai.ChatCompletion.create(
        model=model,
        messages=dialog,
        temperature=temperature, 
        max_tokens=max_tokens,
        functions = functions
    )

    if keep_response:
        return response['choices'][0]['message']
    return response['choices'][0]['message']['content']
    
class GPTApiView(APIView):
    # authentication_classes = [authentication.TokenAuthentication]
    # permission_classes = [permissions.IsAuthenticated]
    def post(self, request, *args, **kwargs):
        # This API just call GPTApi then return result 
        messages = request.data.get('messages')
        dialog = [
            {"role": "system", "content": "Bạn là một chuyên gia đề xuất ẩm thực cho khách hàng.\n Khi trả lời, bạn chỉ nên nói một ý một lúc, ví dụ khi gợi ý về món ăn thì không nen hỏi câu khác.\n Khi khách hàng hỏi về món ăn, bạn nên gợi ý khoảng 7 món ăn dựa trên hoàn cảnh.\n Sau đó, bạn có gợi ý thêm về loại ẩm thực như châu Âu, châu Á hoặc cụ thể hơn là Món Hàn, Món Thái dựa trên lựa chọn của khách hàng.\n Hỏi thêm thông tin từ khách hàng muốn tìm quán ở khu vực nào, nếu thiếu.\n Đừng tự ý thêm thông tin khi đưa vào functions."},
            # {"role": "assistant", "content": "Xin chào khách hàng thân mến,\n\nTôi là chuyên gia đề xuất ẩm thực của bạn và rất hân hạnh được phục vụ bạn. Tôi hy vọng tôi có thể giúp bạn tìm kiếm các món ăn ngon và phù hợp với khẩu vị của bạn. Hãy cùng bắt đầu cuộc trò chuyện để tìm ra những món ăn tuyệt vời nhất cho bạn nhé!"}
        ]

        functions = [
            {
                "name": "GetRestaurants",
                "description": "lấy các nhà hàng từ database dựa trên yêu cầu của khách hàng. Trước khi gọi function GetRestaurants phải lấy đủ thông tin từ khách hàng.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "districts": {
                            "type": "string",
                            "description": "Một quận, huyện ở thành phố Hồ Chí Minh, hỏi lại khách hàng nếu chưa có thông tin. Ví dụ: Quận Bình Thạnh, Quận 5.",
                        },
                        "cuisines": {
                            "type": "string",
                            "description": "Một hay nhiều món ăn ẩm thực như: Món Việt, Món Hàn, Brazil mà khách hàng chọn.",
                        }
                    },
                    "required": ["districts", "cuisines"],
                },
            },
        ]
        
        dialog += messages

        data = ChatGPT(
            dialog=remove_payload(dialog),
            functions=functions,
            keep_response=True,
            model="gpt-3.5-turbo-0613"
        )
        if data.get("function_call"):
            params = json.loads(data['function_call']['arguments'])
            response_obj = foody_search.GetRestaurants(
                cuisines = params.get("cuisines"),
                districts = params.get("districts"),
                debug=False
            )
            dialog.append({
                "role": "assistant",
                "content":{
                    "text": response_obj['restaurants_response'],
                    "payload": response_obj['add_info_res']
                }
            })
        else:
            dialog.append(data)
        return Response(dialog[-1], status=status.HTTP_200_OK)
    


# def detail(request, question_id):
#     try:
#         question = Question.objects.get(pk=question_id)
#     except Question.DoesNotExist:
#         raise Http404("Question does not exist")
#     return render(request, "chatbot/detail.html", {"question": question})


# def results(request, question_id):
#     question = get_object_or_404(Question, pk=question_id)
#     return render(request, "chatbot/results.html", {"question": question})
#     # response = "You're looking at the results of question %s."
#     # return HttpResponse(response % question_id)


# def vote(request, question_id):
#     question = get_object_or_404(Question, pk=question_id)
#     try:
#         selected_choice = question.choice_set.get(pk=request.POST["choice"])
#     except (KeyError, Choice.DoesNotExist):
#         # Redisplay the question voting form.
#         return render(
#             request,
#             "polls/detail.html",
#             {
#                 "question": question,
#                 "error_message": "You didn't select a choice.",
#             },
#         )
#     else:
#         selected_choice.votes += 1
#         selected_choice.save()
#         # Always return an HttpResponseRedirect after successfully dealing
#         # with POST data. This prevents data from being posted twice if a
#         # user hits the Back button.
#         return HttpResponseRedirect(reverse("chatbot:results", args=(question.id,)))

# def index(request):
#     latest_question_list = Question.objects.order_by("-pub_date")[:5]
#     output = ", ".join([q.question_text for q in latest_question_list])
#     return HttpResponse(output)

# from .models import Todo
# from .serializers import TodoSerializer

# class TodoListApiView(APIView):
#     # add permission to check if user is authenticated
#     permission_classes = [permissions.IsAdminUser]

#     # 1. List all
#     def get(self, request, *args, **kwargs):
#         '''
#         List all the todo items for given requested user
#         '''
#         todos = Todo.objects.filter(user = request.user.id)
#         serializer = TodoSerializer(todos, many=True)
#         return Response(serializer.data, status=status.HTTP_200_OK)

#     # 2. Create
#     def post(self, request, *args, **kwargs):
#         '''
#         Create the Todo with given todo data
#         '''
#         data = {
#             'task': request.data.get('task'), 
#             'completed': request.data.get('completed'), 
#             'user': request.user.id
#         }
#         serializer = TodoSerializer(data=data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_201_CREATED)

#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)