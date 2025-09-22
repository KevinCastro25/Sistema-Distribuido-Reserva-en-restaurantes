import unittest
import json
from app import create_app
from models.usuario import db, Usuario

class TestAuthEndpoints(unittest.TestCase):
    
    def setUp(self):
        """Configuración antes de cada test"""
        self.app = create_app('default')
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        
        self.client = self.app.test_client()
        
        with self.app.app_context():
            db.create_all()
    
    def tearDown(self):
        """Limpieza después de cada test"""
        with self.app.app_context():
            db.session.remove()
            db.drop_all()
    
    def test_registro_exitoso(self):
        """Test: Registro de usuario exitoso"""
        data = {
            'nombre': 'Test User',
            'email': 'test@example.com',
            'password': 'password123'
        }
        
        response = self.client.post('/api/auth/register',
                                   data=json.dumps(data),
                                   content_type='application/json')
        
        self.assertEqual(response.status_code, 201)
        self.assertIn('Usuario registrado con éxito', response.get_json()['message'])
    
    def test_registro_email_duplicado(self):
        """Test: Error al registrar email duplicado"""
        data = {
            'nombre': 'Test User',
            'email': 'test@example.com',
            'password': 'password123'
        }
        
        # Primer registro
        self.client.post('/api/auth/register',
                        data=json.dumps(data),
                        content_type='application/json')
        
        # Segundo registro (debería fallar)
        response = self.client.post('/api/auth/register',
                                   data=json.dumps(data),
                                   content_type='application/json')
        
        self.assertEqual(response.status_code, 400)
        self.assertIn('ya está registrado', response.get_json()['message'])
    
    def test_login_exitoso(self):
        """Test: Login exitoso"""
        # Crear usuario primero
        with self.app.app_context():
            user = Usuario('Test User', 'test@example.com', 'password123')
            db.session.add(user)
            db.session.commit()
        
        # Intentar login
        data = {
            'email': 'test@example.com',
            'password': 'password123'
        }
        
        response = self.client.post('/api/auth/login',
                                   data=json.dumps(data),
                                   content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('token', response.get_json())
    
    def test_login_credenciales_invalidas(self):
        """Test: Login con credenciales inválidas"""
        data = {
            'email': 'noexiste@example.com',
            'password': 'wrongpassword'
        }
        
        response = self.client.post('/api/auth/login',
                                   data=json.dumps(data),
                                   content_type='application/json')
        
        self.assertEqual(response.status_code, 401)
        self.assertIn('Credenciales inválidas', response.get_json()['message'])
    
    def test_perfil_con_token_valido(self):
        """Test: Obtener perfil con token válido"""
        # Crear usuario
        with self.app.app_context():
            user = Usuario('Test User', 'test@example.com', 'password123')
            db.session.add(user)
            db.session.commit()
            token = user.generate_token()
        
        # Obtener perfil
        response = self.client.get('/api/auth/perfil',
                                  headers={'Authorization': f'Bearer {token}'})
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()['user']['email'], 'test@example.com')
    
    def test_perfil_sin_token(self):
        """Test: Error al obtener perfil sin token"""
        response = self.client.get('/api/auth/perfil')
        
        self.assertEqual(response.status_code, 401)
        self.assertIn('Token faltante', response.get_json()['message'])

def run_tests():
    """Ejecuta todos los tests"""
    print("🧪 Ejecutando tests del backend...\n")
    
    # Configurar el runner de tests
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestAuthEndpoints)
    runner = unittest.TextTestRunner(verbosity=2)
    
    # Ejecutar tests
    result = runner.run(suite)
    
    # Resumen
    print(f"\n📊 Resumen:")
    print(f"✅ Tests exitosos: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"❌ Tests fallidos: {len(result.failures)}")
    print(f"💥 Errores: {len(result.errors)}")
    
    return result.wasSuccessful()

if __name__ == '__main__':
    run_tests()