from ramen.models import *

all_char = Character.objects.filter(player=None)

for char in all_char:
  # Update all majors and minors
  print(f"{char.first_name} {char.last_name} {char.nick_name} {char.pronouns}")
  
  ex = Grade.objects.filter(student=char, subject=13)

  if ex.exists():
    print(f"It's already set to {ex[0].grade}")
  else:
    print("Communications: ")
    grade = input("Grade: ")
    new = Grade()
    new.student = char
    new.subject_id = 13
    new.grade = int(grade)
    new.save()
    print("Saved")
  # if ex.grade != 7:
  #   print("you already set this")
  # else:
  #   print("What should I set the major to?")
  #   grade = input("Grade: ")
  #   ex.grade = int(grade)
  #   ex.save()

  # ex = Grade.objects.get(student=char, subject=char.minor)
  # if ex.grade != 5:
  #   print("you already set this")
  # else:
  #   print("What should I set the minor to?")
  #   grade = input("Grade: ")
  #   ex.grade = int(grade)
  #   ex.save()
