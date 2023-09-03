from flask_login import UserMixin

class User(UserMixin):
    def __init__(self, id):
        self.id = id
        print("UserMixin :",self.id)
    # @staticmethod
    # def get(self):
    #     # 이 메서드를 사용하여 사용자를 가져올 수 있습니다.
    #     # 이 예제에서는 간단하게 사용자의 ID로 가져오는 것을 보여줍니다.
    #     # 실제로는 데이터베이스에서 사용자를 검색하게 됩니다.
    #     if self.email == 'jupsoops@naver.com':
    #         return User(self.email)
    #     return None  # 사용자가 없으면 None을 반환