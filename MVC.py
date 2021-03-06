'''定义模块的基本结构——MVC结构

类Model定义了数据存取操作
抽象类View_Controller的子类定义了交互界面以及Model和View之间的交互
'''

import pymysql
import abc
from RSA_AES import key_generate, aes_encrypt, aes_decrypt
import wx

class Model(object):
    '''定义了所有与数据库交互的操作'''
    @staticmethod
    def get_con():
        '''建立数据库联系，返回连接和游标'''
        try:
            conn = pymysql.connect(
                host='127.0.0.1'
                ,user='root'
                ,port=3306
                ,passwd='002189xhxXHX'
                ,db='库存管理系统'
                ,charset='utf8'
            )
            cur = conn.cursor()
            return conn,cur
        except Exception as e:
            print('连接时产生错误：',e)

###############完成登录注册功能######################
    def get_all_adminName(self)->list[str]:
        '''获取所有管理员姓名'''
        conn,cur = Model.get_con()
        try:
            sql_pattern = """
                            SELECT adminName FROM adminsinfo
                            """
            sql = sql_pattern
            cur.execute(sql)
            result = cur.fetchall()
            name_list = []
            for i in result:
                name_list.append(i[0])
            return name_list
        except Exception as e:
            print('获取所有管理员姓名时产生错误：',e)
        finally:
            cur.close()
            conn.close()
    
    def Admin_register(self,adminName:str,password:str,sex:str)->bool:
        '''完成管理员注册
        
        adminName为管理员姓名，sex为其性别
        password为输入的密码，密码会在经过RSA、AES混合加密后被存入数据库
        
        返回布尔值，若注册成功，返回True；否则返回False'''
        conn,cur = Model.get_con()
        # 生成一对密钥
        ## filename为存储私钥的文件名称
        public_key, _ = key_generate(adminName)
        if not public_key:
            return False
        # 对输入的密码进行加密
        filename = aes_encrypt(adminName, password,public_key)
        if not filename:
            return False
        try:
            sql_pattern = """
                            INSERT INTO adminsinfo(adminName,Sex,filename)
                            Values('{0}','{1}','{2}')  
                            """
            sql = sql_pattern.format(adminName,sex,filename)
            # print(sql)
            cur.execute(sql)
            conn.commit()
            return True
        except Exception as e:
            print('用户注册时产生错误:',e)
            conn.rollback()
            return False
        finally:
            cur.close()
            conn.close()
    
    def Admin_login(self,adminName:str,password:str,private_key:str)->bool:
        '''进行用户登录验证
        
        正确则返回adminID，错误则返回False'''

        conn,cur = Model.get_con()
        try:
            sql_pattern = """
                            SELECT * FROM adminsinfo
                            WHERE adminName='{0}'
                            """
            sql = sql_pattern.format(adminName)
            cur.execute(sql)
            result = cur.fetchone()
            # 对输入的密码进行验证
            if result:
                # 获取保存加密后的密码的文件名
                filename = result[3]
                # 对数据库中的密码进行解密
                password_decrypted = aes_decrypt(filename,private_key)
                # 对输入的密码进行验证
                if password_decrypted == password:
                    return result[0]  #返回adminID
                else:
                    return False
            else:
                return False
        except Exception as e:
            print('用户登录时产生错误错误：',e)
        finally:
            cur.close()
            conn.close()
    
    def change_password(self,adminID:str,old_password:str,new_password:str, private_key:str)->bool:
        '''修改密码
        
        adminID为管理员ID，old_password为旧密码，new_password为新密码
        
        先对数据中的密码进行解密，并验证输入的旧密码的正确性；
        再对新密码进行加密，并将加密后的密码写入数据库
        若成功修改，返回True，否则返回False'''
        con,cur = Model.get_con()
        try:
            # 对旧密码进行正确性验证
            sql_pattern = """
                            SELECT * FROM adminsinfo
                            WHERE adminID='{0}'
                            """
            sql = sql_pattern.format(adminID)
            cur.execute(sql)
            result = cur.fetchone()
            ## 对输入的密码进行哈希加密验证
            if result:
                # 获取保存加密后的密码的文件名
                filename = result[3]
                # 获取用户名
                adminName = result[1]
                # 对数据库中的密码进行解密
                password_decrypted = aes_decrypt(filename,private_key)
                ## 对输入的旧密码进行验证
                if old_password != password_decrypted:
                    return False
                else:
                    ## 先生成钥匙对
                    public_key, _ = key_generate(adminName=adminName)
                    ## 用生成的公钥对新密码进行加密
                    filename = aes_encrypt(adminName, new_password,public_key)
                    sql_pattern = """
                                    update adminsinfo 
                                    set filename='{0}'
                                    where adminID='{1}'
                                    """
                    sql = sql_pattern.format(filename, adminID)
                    cur.execute(sql)
                    con.commit()
                    return True
        except Exception as e:
            print('修改密码时产生错误：',e)
            con.rollback()
        finally:
            cur.close()
            con.close()
    
###############完成商品信息管理功能######################
    def get_goods_info(self)->list:
        '''获取商品信息'''
        conn,cur = Model.get_con()
        try:
            sql_pattern = """
                            SELECT * FROM products
                            """
            sql = sql_pattern.format()
            cur.execute(sql)
            result = cur.fetchall()
            products_list = []
            for i in result:
                products_list.append(i)
            return products_list
        except Exception as e:
            print('获取商品信息时产生错误：',e)
        finally:
            cur.close()
            conn.close()
    
    def get_available_goods_info(self)->list[str]:
        '''获取未上架的商品ID列表'''
        conn,cur = Model.get_con()
        try:
            sql = """SELECT productID FROM products WHERE isPlaced=FALSE"""
            cur.execute(sql)
            result = cur.fetchall()
            vailable_productIDs_list = []
            for i in result:
                vailable_productIDs_list.append(str(i[0]))
            return vailable_productIDs_list
        except Exception as e:
            print('获取未上架的商品ID列表时产生错误：',e)
        finally:
            cur.close()
            conn.close()

    def add_good_info(self,productName:str,unitPrice:float,unitInStock:int):
        '''添加商品信息
        
        productName为商品名称，unitPrice为商品单价，unitInStock为商品库存'''
        conn,cur = Model.get_con()
        try:
            sql_pattern = """
                            call add_product('{0}',{1},{2}) 
                            """
            sql = sql_pattern.format(productName,unitPrice,unitInStock)
            # print(sql)
            cur.execute(sql)
            conn.commit()
        except Exception as e:
            print('添加商品信息时产生错误:',e)
            conn.rollback()
        finally:
            cur.close()
            conn.close()

    def alter_good_info(self,productID:int,productName:str,unitPrice:float,unitInStock:int):
        '''修改商品信息'''
        conn,cur = Model.get_con()
        try:
            sql_pattern = """
                            call alter_product({0},'{1}',{2},{3}) 
                            """
            sql = sql_pattern.format(productID,productName,unitPrice,unitInStock)
            # print(sql)
            cur.execute(sql)
            conn.commit()
        except Exception as e:
            print('修改商品信息时产生错误:',e)
            conn.rollback()
        finally:
            cur.close()
            conn.close()
    
    def delete_good_info(self,productID:int):
        '''删除商品信息
        
        （若商品还放在货架上，即该商品在库存信息表items中还有外键引用，则会触发触发器del_product_del_item，将该商品从库存信息表items中删除）'''
        conn,cur = Model.get_con()
        try:
            sql_pattern = """call del_product({0})"""
            sql = sql_pattern.format(productID)
            cur.execute(sql)
            conn.commit()
        except Exception as e:
            print('删除商品信息时产生错误:',e)
            conn.rollback()
        finally:
            cur.close()
            conn.close()
    
###############完成货架信息管理功能######################
    def get_shelves_info(self)->list:
        '''获取货架信息'''
        conn,cur = Model.get_con()
        try:
            sql_pattern = """
                            SELECT * FROM shelves
                            """
            sql = sql_pattern.format()
            cur.execute(sql)
            result = cur.fetchall()
            shelves_list = []
            for i in result:
                shelves_list.append(i)
            return shelves_list
        except Exception as e:
            print('获取货架信息时产生错误：',e)
        finally:
            cur.close()
            conn.close()

    def get_available_shelves(self)->list[str]:
        '''获取可用的货架ID列表'''
        conn, cur = Model.get_con()
        try:
            sql = """SELECT shelfID FROM shelves WHERE isUsed=FALSE"""
            cur.execute(sql)
            result = cur.fetchall()
            vailable_shelves = []
            for i in result:
                vailable_shelves.append(str(i[0]))
            return vailable_shelves
        except Exception as e:
            print('获取可用的货架ID列表时产生错误：', e)
        finally:
            cur.close()
            conn.close()

    def add_shelf_info(self,shelfLocation:str):
        '''添加货架位置信息
        
        shelflocation表示货架位置'''
        conn,cur = Model.get_con()
        try:
            sql_pattern = """call add_shelves('{0}')"""
            sql = sql_pattern.format(shelfLocation)
            cur.execute(sql)
            conn.commit()
        except Exception as e:
            print('添加货架位置信息时产生错误:',e)
            conn.rollback()
        finally:
            cur.close()
            conn.close()
    
    def alter_shelf_info(self,shelfID:int,shelfLocation:str):
        '''修改货架位置信息'''
        conn, cur = Model.get_con()
        try:
            sql_pattern = """call alter_shelves({0},'{1}')"""
            sql = sql_pattern.format(shelfID,shelfLocation)
            cur.execute(sql)
            conn.commit()
        except Exception as e:
            print('修改货架位置信息时产生错误:',e)
            conn.rollback()
        finally:
            cur.close()
            conn.close()
    
    def del_shelf_info(self,shelfID:int)->bool:
        '''删除货架位置信息
        
        （若货架上有商品，即该货架上有商品信息表items中还有外键引用，此时货架信息中的isUsed为True，货架信息不能删除，返回False）'''
        conn,cur = Model.get_con()
        try:
            sql_pattern = """select isUsed from shelves where shelfID = {0}"""
            sql = sql_pattern.format(shelfID)
            cur.execute(sql)
            result = cur.fetchone()
            if result[0] == True:
                return False #货架上有商品，不能删除
            else:  #货架上没有商品，开始进行删除操作
                sql_pattern2 = """call del_shelves({0})"""
                sql2 = sql_pattern2.format(shelfID)
                cur.execute(sql2)
                conn.commit()
                return True
        except Exception as e:
            print('删除货架信息时产生错误:',e)
            conn.rollback()
        finally:
            cur.close()
            conn.close()

###############完成库存信息管理功能######################
    def get_items_info(self)->list:
        '''获取库存信息，调用视图items_report_detailed'''
        conn,cur = Model.get_con()
        try:
            sql_pattern = """select * from items_report_detailed"""
            sql = sql_pattern.format()
            cur.execute(sql)
            result = cur.fetchall()
            items_list = []
            for i in result:
                items_list.append(i)
            return items_list
        except Exception as e:
            print('获取库存信息时产生错误：',e)
        finally:
            cur.close()
            conn.close()

    def add_item_info(self,productID:int,shelfID:int,adminID:int):
        '''商品入库管理

        productID为商品ID，shelfID为货架ID，adminID为管理员ID,即添加库存信息的操作员ID'''
        conn,cur = Model.get_con()
        try:
            sql_pattern = """call add_items({0},{1},{2})"""
            sql = sql_pattern.format(productID,shelfID,adminID)
            cur.execute(sql)
            conn.commit()
        except Exception as e:
            print('添加库存信息时产生错误:',e)
            conn.rollback()
        finally:
            cur.close()
            conn.close()
    
    def del_item_info(self,productID:int,shelfID:int):
        '''商品出库管理'''
        conn,cur = Model.get_con()
        try:
            sql_pattern = """call del_items({0},{1})"""
            sql = sql_pattern.format(productID,shelfID)
            cur.execute(sql)
            conn.commit()
        except Exception as e:
            print('删除库存信息时产生错误:',e)
            conn.rollback()
        finally:
            cur.close()
            conn.close()


class View_Controller(metaclass=abc.ABCMeta):
    class Window(wx.Frame):
        def __init__(self) -> None:
            '''初始化页面'''
            raise NotImplementedError

        @abc.abstractmethod
        def populate_data(self):
            '''将数据显示到页面上'''
            raise NotImplementedError

        @abc.abstractmethod
        def onInsert(self):
            '''触发数据插入事件'''
            raise NotImplementedError
        
        @abc.abstractmethod
        def onUpdate(self):
            '''触发数据更新事件'''
            raise NotImplementedError
        
        @abc.abstractmethod
        def onDelete(self):
            '''触发数据删除事件'''
            raise NotImplementedError


if __name__ == '__main__':
    model = Model()
    # model.Admin_register('李四','男','123456')
    info = model.get_goods_info()
    print(list(zip(*info))[1])
    print(list(zip(i for i in info))[1])