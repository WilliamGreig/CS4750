import pymysql
import die.settings
import die.models

# sql prevention


def connect():
    db = pymysql.connect(host=die.settings.MYSQL_DATABASE_HOST, user=die.settings.MYSQL_DATABASE_USER,
            password=die.settings.MYSQL_DATABASE_PASSWORD, database=die.settings.MYSQL_DATABASE_NAME)
    return db

    

def get_players():
    db = connect()
    cursor = db.cursor()
    sql = "SELECT * FROM Player"
    
    try:
        cursor.execute(sql)
        results = cursor.fetchall()
        
        
    except Exception as e:
        print(e)
        
    db.close()
    
def authenticate_user(username, hash):
    db = connect()
    cursor = db.cursor()
    sql = "SELECT * FROM Admin WHERE username = '" + str(username) + "' AND hash = '" + str(hash) + "';"

    try:
        cursor.execute(sql)
        result = cursor.fetchone()
        
        if result != None:
            return True

    except Exception as e:
        print(sql, e)

    return False
   
def get_user_priv(username):
    db = connect()
    cursor = db.cursor()
    sql = "SELECT * FROM Admin;"
    cursor.execute(sql)
    result = cursor.fetchone()
    print(result)
    
    sql = "SELECT * FROM Admin WHERE username = '" + str(username) + "';"

    try:
        cursor.execute(sql)
        result = cursor.fetchone()
        
        return result[2]
        
    except Exception as e:
        print(sql, e)
    
    return -1

def create_SQL(sql, f):
    if len(f) > 0:
        sql += "WHERE "
        
    for i in f.keys():
        sql += i + " = '" + str(f[i]) + "' AND "

    # remove last AND
    if len(f) > 0:
        sql = sql[:-4]
    return sql
    
def get_options(m):
    out = []
    for i in m:
        out.append((i.id, str(i)))
    return out
 

class Relationship(object):
    model_a = None
    model_b = None
    
    @classmethod
    def get_by_a(cls, a_id):
        db = connect()
        cursor = db.cursor()
        
        sql = "SELECT * FROM " + str(cls.__name__) + " WHERE " + (cls.model_a.__name__).lower()[1:] + "_id = '" + str(a_id) + "'"
    
        #print(sql)
        try:
            cursor.execute(sql)
            results = cursor.fetchall()
            out = []
            
            for r in results:
                if (r != None):
                    out.append(cls.model_b.get({'id': r[1]}))
            
            return out
            
        except Exception as e:
            print(e)
        
    
    @classmethod
    def get_by_b(cls, b_id):
        db = connect()
        cursor = db.cursor()
        
        sql = "SELECT * FROM " + str(cls.__name__) + " WHERE " + (cls.model_b.__name__).lower()[1:] + "_id = '" + str(b_id) + "'"
    
        #print(sql)
        try:
            cursor.execute(sql)
            results = cursor.fetchall()
            out = []
            
            for r in results:
                if (r != None):
                    out.append(cls.model_a.get({'id': r[0]}))
            
            return out
            
        except Exception as e:
            print(e)
        
    @classmethod
    def insert(cls, a_id, b_id):
        db = connect()
        cursor = db.cursor()
        sql = "INSERT INTO " + str(cls.__name__) + " values (" + str(a_id) + ", " + str(b_id) + ")"
    
        #print(sql)
        try:
            cursor.execute(sql)
            db.commit()
        except Exception as e:
            print(sql, e)
            db.rollback()
        
        db.close()
    
class Model(object):
    
    fields = []
    
    
    def table(self):
        if type(self) == die.models.Player:
            return "Player"
    
    
    def __init__(self):
        self.id = -1
        
    def delete(self):
        db = connect()
        cursor = db.cursor()
        sql = "DELETE FROM " + str(type(self).__name__)[1:] + " WHERE id = " + str(self.id) 
                        
        #print(sql)
        try:
            cursor.execute(sql)
            db.commit()
        except Exception as e:
            print(sql, e)
            db.rollback()
           
        db.close()
        
    # UPDATE FOR ADMIN TABLE for passwords -- needs slightly different implementation
    def updateA(self):
        db = connect()
        cursor = db.cursor()

        sql = "UPDATE " + str(type(self).__name__)[1:] + " SET hash=MD5('" + str(self.hash) + "') WHERE username='" + str(self.username) + "'"
        print(sql)
        
        try:
            print(sql)
            cursor.execute(sql)
            db.commit()
        except Exception as e:
            print(sql, e)
            db.rollback()

        db.close()
        
    # UPDATE FOR ADMIN TABLE privilege
    def updateAPriv(self):
        db = connect()
        cursor = db.cursor()

        sql = "UPDATE " + str(type(self).__name__)[1:] + " SET privilege='" + str(self.privilege) + "' WHERE username='" + str(self.username) + "'"
        
        try:
            print(sql)
            cursor.execute(sql)
            db.commit()
        except Exception as e:
            print(sql, e)
            db.rollback()

        db.close()
        
    # select all for admin table -- needs diff. impl cuz no id
    def allAdmin():
        db = connect()
        cursor = db.cursor()
        
        
        sql = "SELECT * FROM Admin"


        try:
            cursor.execute(sql)
            results = cursor.fetchall()
            return results
            
        except Exception as e:
            print(sql, e)
        
        db.close()
        
    
    def save(self):
        db = connect()
        cursor = db.cursor()

        sql = "SELECT username FROM Admin"
        admin_list = []
        cursor.execute(sql)
        results = cursor.fetchall()
        for i in results:
            admin_list.append(i[0])
        
        
        if self.id == -1:
            sql = "INSERT INTO " + str(type(self).__name__)[1:] + "("
            for k in type(self).fields.keys():
                sql += k + ", "
            sql = sql[:-2] + ") VALUES ("
            
            for k in type(self).fields.keys():
                if not getattr(self, k) == None:
                    sql += "'" + str(getattr(self, k)) + "', "
                else:
                    sql += "NULL, "
            
            sql = sql[:-2] + ")"

        
        else:
            sql = "UPDATE " + str(type(self).__name__)[1:] + " SET "
            
            # https://stackoverflow.com/questions/11637293/iterate-over-object-attributes-in-python -- get attributes
            
            for k in type(self).fields.keys():
                if not getattr(self, k) == None:
                    sql += k + " = '" + str(getattr(self, k)) + "', "
                else:
                    sql += k + " = NULL, "
                
            sql = sql[:-2]
            
            sql += " WHERE id = '" + str(self.id) + "'"
        
        try:
            print(sql)
            cursor.execute(sql)
            db.commit()
        except Exception as e:
            print(sql, e)
            db.rollback()
           
        if self.id == -1:
            cursor.execute("SELECT LAST_INSERT_ID()")
            self.id = cursor.fetchone()[0]
        
           
        db.close()

        
    
    @classmethod
    def all(cls):
        return cls.filter({})

      
    @classmethod
    def filter(cls, f):
        
        db = connect()
        cursor = db.cursor()
        
        
        sql = "SELECT * FROM " + str(cls.__name__)[1:] + " "
        sql = create_SQL(sql, f)
        

        try:
            cursor.execute(sql)
            results = cursor.fetchall()
            
            outs = []
            
            for result in results:
                # reference: https://www.programiz.com/python-programming/methods/built-in/setattr --- set attributes of class dynamically
                out = cls()
                
                
                setattr(out, "id", result[0])
                i = 1
                for k in cls.fields.keys():
                    setattr(out, k, result[i])
                    i += 1
                
                outs.append(out)
            
            return outs
            
            
        except Exception as e:
            print(sql, e)
        
        db.close()
      
    @classmethod
    def get(cls, f):
        
        db = connect()
        cursor = db.cursor()
        
        sql = "SELECT * FROM " + str(cls.__name__)[1:]  + " "
        sql = create_SQL(sql, f)

        try:
            cursor.execute(sql)
            result = cursor.fetchone()
            
            # reference: https://www.programiz.com/python-programming/methods/built-in/setattr --- set attributes of class dynamically
            out = cls()
            
            
            setattr(out, "id", result[0])
            i = 1
            for k in cls.fields.keys():
                setattr(out, k, result[i])
                i += 1
            
            return out
            
            
        except Exception as e:
            print(sql, e)
        
        db.close()
    
    
    