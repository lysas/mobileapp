from app.evaluation.evaluate import evaluate_answer

student_answer = "1.a Photosynthesis is the process by which green plants make food using sunlight."

result = evaluate_answer("1-a", student_answer)

print(result)
