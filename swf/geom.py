import math

SNAP = 0.001

class Vector2(object):
    def __init__(self, x=0.0, y=0.0):
        self.x = x
        self.y = y
        
class Vector3(object):
    def __init__(self, x=0, y=0, z=0):
        self.x = x
        self.y = y
        self.z = z
    
    def clone(self):
        return Vector3(self.x, self.y, self.z)
    
    def cross(self, v1, v2):
        self.x = v1.y * v2.z - v1.z * v2.y
        self.y = v1.z * v2.x - v1.x * v2.z
        self.z = v1.x * v2.y - v1.y * v2.x
        return self
    
    def distance(self, v):
        dx = self.x - v.x
        dy = self.y - v.y
        dz = self.z - v.z
        return math.sqrt(dx*dx + dy*dy + dz*dz)
    
    def distanceSq(self, v):
        dx = self.x - v.x
        dy = self.y - v.y
        dz = self.z - v.z
        return (dx*dx + dy*dy + dz*dz)
    
    def dot(self, v):
        return self.x * v.x + self.y * v.y + self.z * v.z
    
    def length(self):
        return math.sqrt(self.x*self.x + self.y*self.y + self.z * self.z)
    
    def lengthSq(self):
        return (self.x*self.x + self.y*self.y + self.z * self.z)
    
    def addScalar(self, s):
        self.x += s
        self.y += s
        self.z += s
        return self
    
    def divScalar(self, s):
        self.x /= s
        self.y /= s
        self.z /= s
        return self
    
    def multScalar(self, s):
        self.x *= s
        self.y *= s
        self.z *= s
        return self
    
    def sub(self, a, b):
        self.x = a.x - b.x
        self.y = a.y - b.y
        self.z = a.z - b.z
        return self
    
    def subScalar(self, s):
        self.x -= s
        self.y -= s
        self.z -= s
        return self
    
    def equals(self, v, e=None):
        e = SNAP if e is None else e
        if v.x > self.x-e and v.x < self.x+e and \
           v.y > self.y-e and v.y < self.y+e and \
           v.z > self.z-e and v.z < self.z+e:
            return True
        else:
            return False
        
    def normalize(self):
        len = self.length()
        if len > 0.0:
            self.multScalar(1.0 / len)
        return self
    
    def set(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    def tostring(self):
        return "%0.3f %0.3f %0.3f" % (self.x, self.y, self.z)
        
class Matrix2(object):
    """
    Matrix2
    """
    def __init__(self, a=1.0, b=0.0, c=0.0, d=1.0, tx=0.0, ty=0.0):
        self.a = a
        self.b = b
        self.c = c 
        self.d = d
        self.tx = tx
        self.ty = ty
        
    def append(self, a, b, c, d, tx, ty):
        a1 = self.a
        b1 = self.b
        c1 = self.c
        d1 = self.d

        self.a  = a*a1+b*c1
        self.b  = a*b1+b*d1
        self.c  = c*a1+d*c1
        self.d  = c*b1+d*d1
        self.tx = tx*a1+ty*c1+self.tx
        self.ty = tx*b1+ty*d1+self.ty
     
    def append_matrix(self, m):
        self.append(m.a, m.b, m.c, m.d, m.tx, m.ty)
    
    def multiply_point(self, vec):
        return [
            self.a*vec[0] + self.c*vec[1] + self.tx,
            self.b*vec[0] + self.d*vec[1] + self.ty
        ]
        
    def prepend(self, a, b, c, d, tx, ty):
        tx1 = self.tx
        if (a != 1.0 or b != 0.0 or c != 0.0 or d != 1.0):
            a1 = self.a
            c1 = self.c
            self.a  = a1*a+self.b*c
            self.b  = a1*b+self.b*d
            self.c  = c1*a+self.d*c
            self.d  = c1*b+self.d*d
        self.tx = tx1*a+self.ty*c+tx
        self.ty = tx1*b+self.ty*d+ty
        
    def prepend_matrix(self, m):
        self.prepend(m.a, m.b, m.c, m.d, m.tx, m.ty)
        
    def rotate(self, angle):
        cos = math.cos(angle)
        sin = math.sin(angle)
        a1 = self.a
        c1 = self.c
        tx1 = self.tx
        self.a = a1*cos-self.b*sin
        self.b = a1*sin+self.b*cos
        self.c = c1*cos-self.d*sin
        self.d = c1*sin+self.d*cos
        self.tx = tx1*cos-self.ty*sin
        self.ty = tx1*sin+self.ty*cos
    
    def scale(self, x, y):
        self.a *= x;
        self.d *= y;
        self.tx *= x;
        self.ty *= y;
     
    def translate(self, x, y):   
        self.tx += x;
        self.ty += y;
              
class Matrix4(object):
    """
    Matrix4
    """
    def __init__(self, data=None):
        if not data is None and len(data) == 16:
            self.n11 = data[0]; self.n12 = data[1]; self.n13 = data[2]; self.n14 = data[3]
            self.n21 = data[4]; self.n22 = data[5]; self.n23 = data[6]; self.n24 = data[7]
            self.n31 = data[8]; self.n32 = data[9]; self.n33 = data[10]; self.n34 = data[11]
            self.n41 = data[12]; self.n42 = data[13]; self.n43 = data[14]; self.n44 = data[15]
        else:
            self.n11 = 1.0; self.n12 = 0.0; self.n13 = 0.0; self.n14 = 0.0
            self.n21 = 0.0; self.n22 = 1.0; self.n23 = 0.0; self.n24 = 0.0
            self.n31 = 0.0; self.n32 = 0.0; self.n33 = 1.0; self.n34 = 0.0
            self.n41 = 0.0; self.n42 = 0.0; self.n43 = 0.0; self.n44 = 1.0
    
    def clone(self):
        return Matrix4(self.flatten())
    
    def flatten(self):
        return [self.n11, self.n12, self.n13, self.n14, \
                self.n21, self.n22, self.n23, self.n24, \
                self.n31, self.n32, self.n33, self.n34, \
                self.n41, self.n42, self.n43, self.n44]
         
    def identity(self):
        self.n11 = 1.0; self.n12 = 0.0; self.n13 = 0.0; self.n14 = 0.0
        self.n21 = 0.0; self.n22 = 1.0; self.n23 = 0.0; self.n24 = 0.0
        self.n31 = 0.0; self.n32 = 0.0; self.n33 = 1.0; self.n34 = 0.0
        self.n41 = 0.0; self.n42 = 0.0; self.n43 = 0.0; self.n44 = 1.0
        return self
    
    def multiply(self, a, b):
        a11 = a.n11; a12 = a.n12; a13 = a.n13; a14 = a.n14
        a21 = a.n21; a22 = a.n22; a23 = a.n23; a24 = a.n24
        a31 = a.n31; a32 = a.n32; a33 = a.n33; a34 = a.n34
        a41 = a.n41; a42 = a.n42; a43 = a.n43; a44 = a.n44
        b11 = b.n11; b12 = b.n12; b13 = b.n13; b14 = b.n14
        b21 = b.n21; b22 = b.n22; b23 = b.n23; b24 = b.n24
        b31 = b.n31; b32 = b.n32; b33 = b.n33; b34 = b.n34
        b41 = b.n41; b42 = b.n42; b43 = b.n43; b44 = b.n44

        self.n11 = a11 * b11 + a12 * b21 + a13 * b31 + a14 * b41
        self.n12 = a11 * b12 + a12 * b22 + a13 * b32 + a14 * b42
        self.n13 = a11 * b13 + a12 * b23 + a13 * b33 + a14 * b43
        self.n14 = a11 * b14 + a12 * b24 + a13 * b34 + a14 * b44

        self.n21 = a21 * b11 + a22 * b21 + a23 * b31 + a24 * b41
        self.n22 = a21 * b12 + a22 * b22 + a23 * b32 + a24 * b42
        self.n23 = a21 * b13 + a22 * b23 + a23 * b33 + a24 * b43
        self.n24 = a21 * b14 + a22 * b24 + a23 * b34 + a24 * b44

        self.n31 = a31 * b11 + a32 * b21 + a33 * b31 + a34 * b41
        self.n32 = a31 * b12 + a32 * b22 + a33 * b32 + a34 * b42
        self.n33 = a31 * b13 + a32 * b23 + a33 * b33 + a34 * b43
        self.n34 = a31 * b14 + a32 * b24 + a33 * b34 + a34 * b44

        self.n41 = a41 * b11 + a42 * b21 + a43 * b31 + a44 * b41
        self.n42 = a41 * b12 + a42 * b22 + a43 * b32 + a44 * b42
        self.n43 = a41 * b13 + a42 * b23 + a43 * b33 + a44 * b43
        self.n44 = a41 * b14 + a42 * b24 + a43 * b34 + a44 * b44
        return self
    
    def multiplyVector3(self, vec):
        vx = vec[0]
        vy = vec[1]
        vz = vec[2]
        d = 1.0 / (self.n41 * vx + self.n42 * vy + self.n43 * vz + self.n44)
        x = (self.n11 * vx + self.n12 * vy + self.n13 * vz + self.n14) * d
        y = (self.n21 * vx + self.n22 * vy + self.n23 * vz + self.n24) * d
        z = (self.n31 * vx + self.n32 * vy + self.n33 * vz + self.n34) * d
        return [x, y, z]
    
    def multiplyVec3(self, vec):
        vx = vec.x 
        vy = vec.y
        vz = vec.z
        d = 1.0 / (self.n41 * vx + self.n42 * vy + self.n43 * vz + self.n44)
        x = (self.n11 * vx + self.n12 * vy + self.n13 * vz + self.n14) * d
        y = (self.n21 * vx + self.n22 * vy + self.n23 * vz + self.n24) * d
        z = (self.n31 * vx + self.n32 * vy + self.n33 * vz + self.n34) * d
        return Vector3(x, y, z)
    
    def multiplyVector4(self, v):
        vx = v[0]; vy = v[1]; vz = v[2]; vw = v[3];

        x = self.n11 * vx + self.n12 * vy + self.n13 * vz + self.n14 * vw;
        y = self.n21 * vx + self.n22 * vy + self.n23 * vz + self.n24 * vw;
        z = self.n31 * vx + self.n32 * vy + self.n33 * vz + self.n34 * vw;
        w = self.n41 * vx + self.n42 * vy + self.n43 * vz + self.n44 * vw;

        return [x, y, z, w];
    
    def det(self):
        #( based on http://www.euclideanspace.com/maths/algebra/matrix/functions/inverse/fourD/index.htm )
        return (
            self.n14 * self.n23 * self.n32 * self.n41-
            self.n13 * self.n24 * self.n32 * self.n41-
            self.n14 * self.n22 * self.n33 * self.n41+
            self.n12 * self.n24 * self.n33 * self.n41+

            self.n13 * self.n22 * self.n34 * self.n41-
            self.n12 * self.n23 * self.n34 * self.n41-
            self.n14 * self.n23 * self.n31 * self.n42+
            self.n13 * self.n24 * self.n31 * self.n42+

            self.n14 * self.n21 * self.n33 * self.n42-
            self.n11 * self.n24 * self.n33 * self.n42-
            self.n13 * self.n21 * self.n34 * self.n42+
            self.n11 * self.n23 * self.n34 * self.n42+

            self.n14 * self.n22 * self.n31 * self.n43-
            self.n12 * self.n24 * self.n31 * self.n43-
            self.n14 * self.n21 * self.n32 * self.n43+
            self.n11 * self.n24 * self.n32 * self.n43+

            self.n12 * self.n21 * self.n34 * self.n43-
            self.n11 * self.n22 * self.n34 * self.n43-
            self.n13 * self.n22 * self.n31 * self.n44+
            self.n12 * self.n23 * self.n31 * self.n44+

            self.n13 * self.n21 * self.n32 * self.n44-
            self.n11 * self.n23 * self.n32 * self.n44-
            self.n12 * self.n21 * self.n33 * self.n44+
            self.n11 * self.n22 * self.n33 * self.n44)
        
    def lookAt(self, eye, center, up):
        x = Vector3(); y = Vector3(); z = Vector3();
        z.sub(eye, center).normalize();
        x.cross(up, z).normalize();
        y.cross(z, x).normalize();
        #eye.normalize()
        self.n11 = x.x; self.n12 = x.y; self.n13 = x.z; self.n14 = -x.dot(eye);
        self.n21 = y.x; self.n22 = y.y; self.n23 = y.z; self.n24 = -y.dot(eye);
        self.n31 = z.x; self.n32 = z.y; self.n33 = z.z; self.n34 = -z.dot(eye);
        self.n41 = 0.0; self.n42 = 0.0; self.n43 = 0.0; self.n44 = 1.0;
        return self;
    
    def multiplyScalar(self, s):
        self.n11 *= s; self.n12 *= s; self.n13 *= s; self.n14 *= s;
        self.n21 *= s; self.n22 *= s; self.n23 *= s; self.n24 *= s;
        self.n31 *= s; self.n32 *= s; self.n33 *= s; self.n34 *= s;
        self.n41 *= s; self.n42 *= s; self.n43 *= s; self.n44 *= s;
        return self
    
    @classmethod
    def inverse(cls, m1):
        # TODO: make this more efficient
        #( based on http://www.euclideanspace.com/maths/algebra/matrix/functions/inverse/fourD/index.htm )
        m2 = Matrix4();
        m2.n11 = m1.n23*m1.n34*m1.n42 - m1.n24*m1.n33*m1.n42 + m1.n24*m1.n32*m1.n43 - m1.n22*m1.n34*m1.n43 - m1.n23*m1.n32*m1.n44 + m1.n22*m1.n33*m1.n44;
        m2.n12 = m1.n14*m1.n33*m1.n42 - m1.n13*m1.n34*m1.n42 - m1.n14*m1.n32*m1.n43 + m1.n12*m1.n34*m1.n43 + m1.n13*m1.n32*m1.n44 - m1.n12*m1.n33*m1.n44;
        m2.n13 = m1.n13*m1.n24*m1.n42 - m1.n14*m1.n23*m1.n42 + m1.n14*m1.n22*m1.n43 - m1.n12*m1.n24*m1.n43 - m1.n13*m1.n22*m1.n44 + m1.n12*m1.n23*m1.n44;
        m2.n14 = m1.n14*m1.n23*m1.n32 - m1.n13*m1.n24*m1.n32 - m1.n14*m1.n22*m1.n33 + m1.n12*m1.n24*m1.n33 + m1.n13*m1.n22*m1.n34 - m1.n12*m1.n23*m1.n34;
        m2.n21 = m1.n24*m1.n33*m1.n41 - m1.n23*m1.n34*m1.n41 - m1.n24*m1.n31*m1.n43 + m1.n21*m1.n34*m1.n43 + m1.n23*m1.n31*m1.n44 - m1.n21*m1.n33*m1.n44;
        m2.n22 = m1.n13*m1.n34*m1.n41 - m1.n14*m1.n33*m1.n41 + m1.n14*m1.n31*m1.n43 - m1.n11*m1.n34*m1.n43 - m1.n13*m1.n31*m1.n44 + m1.n11*m1.n33*m1.n44;
        m2.n23 = m1.n14*m1.n23*m1.n41 - m1.n13*m1.n24*m1.n41 - m1.n14*m1.n21*m1.n43 + m1.n11*m1.n24*m1.n43 + m1.n13*m1.n21*m1.n44 - m1.n11*m1.n23*m1.n44;
        m2.n24 = m1.n13*m1.n24*m1.n31 - m1.n14*m1.n23*m1.n31 + m1.n14*m1.n21*m1.n33 - m1.n11*m1.n24*m1.n33 - m1.n13*m1.n21*m1.n34 + m1.n11*m1.n23*m1.n34;
        m2.n31 = m1.n22*m1.n34*m1.n41 - m1.n24*m1.n32*m1.n41 + m1.n24*m1.n31*m1.n42 - m1.n21*m1.n34*m1.n42 - m1.n22*m1.n31*m1.n44 + m1.n21*m1.n32*m1.n44;
        m2.n32 = m1.n14*m1.n32*m1.n41 - m1.n12*m1.n34*m1.n41 - m1.n14*m1.n31*m1.n42 + m1.n11*m1.n34*m1.n42 + m1.n12*m1.n31*m1.n44 - m1.n11*m1.n32*m1.n44;
        m2.n33 = m1.n13*m1.n24*m1.n41 - m1.n14*m1.n22*m1.n41 + m1.n14*m1.n21*m1.n42 - m1.n11*m1.n24*m1.n42 - m1.n12*m1.n21*m1.n44 + m1.n11*m1.n22*m1.n44;
        m2.n34 = m1.n14*m1.n22*m1.n31 - m1.n12*m1.n24*m1.n31 - m1.n14*m1.n21*m1.n32 + m1.n11*m1.n24*m1.n32 + m1.n12*m1.n21*m1.n34 - m1.n11*m1.n22*m1.n34;
        m2.n41 = m1.n23*m1.n32*m1.n41 - m1.n22*m1.n33*m1.n41 - m1.n23*m1.n31*m1.n42 + m1.n21*m1.n33*m1.n42 + m1.n22*m1.n31*m1.n43 - m1.n21*m1.n32*m1.n43;
        m2.n42 = m1.n12*m1.n33*m1.n41 - m1.n13*m1.n32*m1.n41 + m1.n13*m1.n31*m1.n42 - m1.n11*m1.n33*m1.n42 - m1.n12*m1.n31*m1.n43 + m1.n11*m1.n32*m1.n43;
        m2.n43 = m1.n13*m1.n22*m1.n41 - m1.n12*m1.n23*m1.n41 - m1.n13*m1.n21*m1.n42 + m1.n11*m1.n23*m1.n42 + m1.n12*m1.n21*m1.n43 - m1.n11*m1.n22*m1.n43;
        m2.n44 = m1.n12*m1.n23*m1.n31 - m1.n13*m1.n22*m1.n31 + m1.n13*m1.n21*m1.n32 - m1.n11*m1.n23*m1.n32 - m1.n12*m1.n21*m1.n33 + m1.n11*m1.n22*m1.n33;
        m2.multiplyScalar(1.0 / m1.det());
        return m2;
    
    @classmethod
    def rotationMatrix(cls, x, y, z, angle):
        rot = Matrix4()
        c = math.cos(angle)
        s = math.sin(angle)
        t = 1 - c
        rot.n11 = t * x * x + c
        rot.n12 = t * x * y - s * z
        rot.n13 = t * x * z + s * y
        rot.n21 = t * x * y + s * z
        rot.n22 = t * y * y + c
        rot.n23 = t * y * z - s * x
        rot.n31 = t * x * z - s * y
        rot.n32 = t * y * z + s * x
        rot.n33 = t * z * z + c
        return rot
    
    @classmethod
    def scaleMatrix(cls, x, y, z):
        m = Matrix4()
        m.n11 = x
        m.n22 = y
        m.n33 = z
        return m
    
    @classmethod
    def translationMatrix(cls, x, y, z):
        m = Matrix4()
        m.n14 = x
        m.n24 = y
        m.n34 = z
        return m
