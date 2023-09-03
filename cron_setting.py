from flask import Flask, render_template, request
from crontab import CronTab

app = Flask(__name__)

@app.route('/schedule', methods=['GET', 'POST'])
def schedule():
    if request.method == 'POST':
        job_comment = request.form.get('job_comment')  # 고객명으로 크론작업 수정에 필요
        day_of_week = request.form.get('day_of_week')  # 요일 값 가져오기

        cron = CronTab(user='your_username')  # 사용자 이름으로 크론탭 생성자 생성
        new_job = cron.new(command='/usr/bin/python3 /usr/src/app/cron_process.py crawl_cron')
        new_job.setall(f'10 0 * * {day_of_week}')  # day_of_week: 1=월, 2=화, 3=수, 4=목, 5=금, 6=토, 0=일
        new_job.set_comment(job_comment)
        cron.write()

        return "크론탭 작업이 등록되었습니다."

    return render_template('./cron_register.html')  # 폼을 보여주는 페이지로 이동

if __name__ == '__main__':
    app.run('0.0.0.0', 8800)
    #app.run()