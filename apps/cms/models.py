from exts import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash


class CMSPersmission(object):
    ALL_PERMISSION = 0b11111111
    # 1.访问者
    VISITOR = 0b00000001
    # 2.管理帖子权限
    POSTER = 0b00000010
    # 3.管理评论的权限
    COMMENTER = 0b00000100
    # 4.管理模块的权限
    BOARDER = 0b00001000
    # 5.管理前台的权限
    FRONTUSER = 0b00010000
    # 6.管理后台的权限
    CMSUSER = 0b00100000


cms_role_user = db.Table(
    'cms_role_user',
    db.Column("cms_role_id", db.Integer, db.ForeignKey("cms_role.id")),
    db.Column("cms_user_id", db.Integer, db.ForeignKey("cms_user.id")),
)


class CMSRole(db.Model):
    __name__ = "cms_role"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50), nullable=False)
    desc = db.Column(db.String(200), nullable=False)
    cteate_time = db.Column(db.DateTime, default=datetime.now)
    permissions = db.Column(db.Integer, default=CMSPersmission.VISITOR)

    users = db.relationship("CMSUser",secondary=cms_role_user,backref="roles")


class CMSUser(db.Model):
    __tablename__ = 'cms_user'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(50), nullable=False)
    _password = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(50), nullable=False, unique=True)
    join_time = db.Column(db.DateTime, default=datetime.now)

    def __init__(self, username, password, email):
        self.username = username
        self.password = password
        self.email = email

    @property
    def password(self):
        return self._password

    @password.setter
    def password(self, raw_password):
        self._password = generate_password_hash(raw_password)

    def check_password(self, raw_password):
        result = check_password_hash(self.password, raw_password)
        return result

    @property
    def permissions(self):
        if not self.roles:
            return 0
        all_permisssions = 0
        for role in self.roles:
            permissions = role.permissions
            all_permisssions |= permissions
        return all_permisssions

    def has_permission(self,permission):
        # all_permissions = self.permissions
        # result = all_permissions&permission ==permission
        return self.permissions&permission == permission

    @property
    def is_developer(self):
        return self.has_permission(CMSPersmission.ALL_PERMISSION)
