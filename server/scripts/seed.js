require('dotenv').config();
const mongoose = require('mongoose');
const User = require('../models/User');

const seedDatabase = async () => {
  try {
    // Conectar ao banco
    await mongoose.connect(process.env.MONGO_URI);
    console.log('Conectado ao MongoDB para seeding');

    // Limpar dados existentes
    await User.deleteMany({});
    console.log('Dados antigos removidos');

    // Criar usuário admin
    const adminUser = new User({
      name: 'Admin',
      email: 'admin@habitus.com',
      password: 'Admin123!',
      role: 'admin'
    });
    await adminUser.save();
    console.log('Usuário admin criado');

    // Criar usuário teste
    const testUser = new User({
      name: 'Usuário Teste',
      email: 'teste@habitus.com',
      password: 'Teste123!',
      role: 'user'
    });
    await testUser.save();
    console.log('Usuário teste criado');

    console.log('Seeding concluído com sucesso');
    process.exit(0);
  } catch (error) {
    console.error('Erro durante o seeding:', error);
    process.exit(1);
  }
};

seedDatabase(); 