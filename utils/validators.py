"""
Validadores para dados do sistema MDM
"""
import re
from typing import List, Optional, Tuple

class DataValidators:
    """Validadores de dados"""
    
    @staticmethod
    def validate_email(email: str) -> Tuple[bool, Optional[str]]:
        """Validar formato de email"""
        if not email:
            return False, "Email é obrigatório"
        
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(pattern, email):
            return False, "Formato de email inválido"
        
        return True, None
    
    @staticmethod
    def validate_cpf(cpf: str) -> Tuple[bool, Optional[str]]:
        """Validar CPF"""
        if not cpf:
            return False, "CPF é obrigatório"
        
        # Remover formatação
        cpf = re.sub(r'\D', '', cpf)
        
        # Verificar se tem 11 dígitos
        if len(cpf) != 11:
            return False, "CPF deve ter 11 dígitos"
        
        # Verificar se não são todos números iguais
        if cpf == cpf[0] * 11:
            return False, "CPF inválido"
        
        # Validar dígitos verificadores
        def calculate_digit(cpf_partial):
            total = sum(int(cpf_partial[i]) * (len(cpf_partial) + 1 - i) for i in range(len(cpf_partial)))
            remainder = total % 11
            return 0 if remainder < 2 else 11 - remainder
        
        if int(cpf[9]) != calculate_digit(cpf[:9]):
            return False, "CPF inválido"
        
        if int(cpf[10]) != calculate_digit(cpf[:10]):
            return False, "CPF inválido"
        
        return True, None
    
    @staticmethod
    def validate_cnpj(cnpj: str) -> Tuple[bool, Optional[str]]:
        """Validar CNPJ"""
        if not cnpj:
            return False, "CNPJ é obrigatório"
        
        # Remover formatação
        cnpj = re.sub(r'\D', '', cnpj)
        
        # Verificar se tem 14 dígitos
        if len(cnpj) != 14:
            return False, "CNPJ deve ter 14 dígitos"
        
        # Verificar se não são todos números iguais
        if cnpj == cnpj[0] * 14:
            return False, "CNPJ inválido"
        
        # Validar primeiro dígito verificador
        weights = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
        total = sum(int(cnpj[i]) * weights[i] for i in range(12))
        remainder = total % 11
        first_digit = 0 if remainder < 2 else 11 - remainder
        
        if int(cnpj[12]) != first_digit:
            return False, "CNPJ inválido"
        
        # Validar segundo dígito verificador
        weights = [6, 7, 8, 9, 2, 3, 4, 5, 6, 7, 8, 9]
        total = sum(int(cnpj[i]) * weights[i] for i in range(13))
        remainder = total % 11
        second_digit = 0 if remainder < 2 else 11 - remainder
        
        if int(cnpj[13]) != second_digit:
            return False, "CNPJ inválido"
        
        return True, None
    
    @staticmethod
    def validate_phone(phone: str) -> Tuple[bool, Optional[str]]:
        """Validar telefone"""
        if not phone:
            return True, None  # Telefone é opcional
        
        # Remover formatação
        phone_digits = re.sub(r'\D', '', phone)
        
        # Verificar se tem 10 ou 11 dígitos (telefone brasileiro)
        if len(phone_digits) not in [10, 11]:
            return False, "Telefone deve ter 10 ou 11 dígitos"
        
        # Verificar se começa com código de área válido
        area_code = phone_digits[:2]
        valid_area_codes = [
            '11', '12', '13', '14', '15', '16', '17', '18', '19',  # SP
            '21', '22', '24',  # RJ
            '27', '28',  # ES
            '31', '32', '33', '34', '35', '37', '38',  # MG
            '41', '42', '43', '44', '45', '46',  # PR
            '47', '48', '49',  # SC
            '51', '53', '54', '55',  # RS
            '61',  # DF
            '62', '64',  # GO
            '63',  # TO
            '65', '66',  # MT
            '67',  # MS
            '68',  # AC
            '69',  # RO
            '71', '73', '74', '75', '77',  # BA
            '79',  # SE
            '81', '87',  # PE
            '82',  # AL
            '83',  # PB
            '84',  # RN
            '85', '88',  # CE
            '86', '89',  # PI
            '91', '93', '94',  # PA
            '92', '97',  # AM
            '95',  # RR
            '96',  # AP
            '98', '99'  # MA
        ]
        
        if area_code not in valid_area_codes:
            return False, "Código de área inválido"
        
        return True, None
    
    @staticmethod
    def validate_cep(cep: str) -> Tuple[bool, Optional[str]]:
        """Validar CEP"""
        if not cep:
            return True, None  # CEP é opcional
        
        # Remover formatação
        cep_digits = re.sub(r'\D', '', cep)
        
        if len(cep_digits) != 8:
            return False, "CEP deve ter 8 dígitos"
        
        return True, None
    
    @staticmethod
    def validate_required_field(value: str, field_name: str) -> Tuple[bool, Optional[str]]:
        """Validar campo obrigatório"""
        if not value or not value.strip():
            return False, f"{field_name} é obrigatório"
        return True, None
    
    @staticmethod
    def validate_price(price: str) -> Tuple[bool, Optional[str]]:
        """Validar preço"""
        if not price:
            return True, None  # Preço pode ser vazio (será 0)
        
        try:
            price_value = float(price)
            if price_value < 0:
                return False, "Preço não pode ser negativo"
            return True, None
        except ValueError:
            return False, "Preço deve ser um número válido"
    
    @staticmethod
    def validate_cliente(data: dict) -> List[str]:
        """Validar dados completos de cliente"""
        errors = []
        
        # Nome obrigatório
        is_valid, error = DataValidators.validate_required_field(data.get('nome', ''), 'Nome')
        if not is_valid:
            errors.append(error)
        
        # Email obrigatório e válido
        is_valid, error = DataValidators.validate_email(data.get('email', ''))
        if not is_valid:
            errors.append(error)
        
        # CPF/CNPJ obrigatório e válido
        cpf_cnpj = data.get('cpf_cnpj', '')
        tipo = data.get('tipo', '')
        
        if not cpf_cnpj:
            errors.append("CPF/CNPJ é obrigatório")
        elif tipo == 'pessoa_fisica':
            is_valid, error = DataValidators.validate_cpf(cpf_cnpj)
            if not is_valid:
                errors.append(error)
        elif tipo == 'pessoa_juridica':
            is_valid, error = DataValidators.validate_cnpj(cpf_cnpj)
            if not is_valid:
                errors.append(error)
        else:
            errors.append("Tipo deve ser 'pessoa_fisica' ou 'pessoa_juridica'")
        
        # Telefone opcional, mas se preenchido deve ser válido
        is_valid, error = DataValidators.validate_phone(data.get('telefone', ''))
        if not is_valid:
            errors.append(error)
        
        # CEP opcional, mas se preenchido deve ser válido
        is_valid, error = DataValidators.validate_cep(data.get('cep', ''))
        if not is_valid:
            errors.append(error)
        
        return errors
    
    @staticmethod
    def validate_produto(data: dict) -> List[str]:
        """Validar dados completos de produto"""
        errors = []
        
        # Nome obrigatório
        is_valid, error = DataValidators.validate_required_field(data.get('nome', ''), 'Nome')
        if not is_valid:
            errors.append(error)
        
        # Código obrigatório
        is_valid, error = DataValidators.validate_required_field(data.get('codigo', ''), 'Código')
        if not is_valid:
            errors.append(error)
        
        # Categoria obrigatória
        is_valid, error = DataValidators.validate_required_field(data.get('categoria', ''), 'Categoria')
        if not is_valid:
            errors.append(error)
        
        # Unidade de medida obrigatória
        is_valid, error = DataValidators.validate_required_field(data.get('unidade_medida', ''), 'Unidade de medida')
        if not is_valid:
            errors.append(error)
        
        # Preço opcional, mas se preenchido deve ser válido
        is_valid, error = DataValidators.validate_price(data.get('preco', ''))
        if not is_valid:
            errors.append(error)
        
        return errors
    
    @staticmethod
    def validate_fornecedor(data: dict) -> List[str]:
        """Validar dados completos de fornecedor"""
        errors = []
        
        # Nome obrigatório
        is_valid, error = DataValidators.validate_required_field(data.get('nome', ''), 'Nome')
        if not is_valid:
            errors.append(error)
        
        # Email obrigatório e válido
        is_valid, error = DataValidators.validate_email(data.get('email', ''))
        if not is_valid:
            errors.append(error)
        
        # CNPJ obrigatório e válido
        is_valid, error = DataValidators.validate_cnpj(data.get('cnpj', ''))
        if not is_valid:
            errors.append(error)
        
        # Telefone opcional, mas se preenchido deve ser válido
        is_valid, error = DataValidators.validate_phone(data.get('telefone', ''))
        if not is_valid:
            errors.append(error)
        
        # CEP opcional, mas se preenchido deve ser válido
        is_valid, error = DataValidators.validate_cep(data.get('cep', ''))
        if not is_valid:
            errors.append(error)
        
        return errors
    
    @staticmethod
    def format_cpf(cpf: str) -> str:
        """Formatar CPF"""
        if not cpf:
            return ""
        
        digits = re.sub(r'\D', '', cpf)
        if len(digits) == 11:
            return f"{digits[:3]}.{digits[3:6]}.{digits[6:9]}-{digits[9:]}"
        return cpf
    
    @staticmethod
    def format_cnpj(cnpj: str) -> str:
        """Formatar CNPJ"""
        if not cnpj:
            return ""
        
        digits = re.sub(r'\D', '', cnpj)
        if len(digits) == 14:
            return f"{digits[:2]}.{digits[2:5]}.{digits[5:8]}/{digits[8:12]}-{digits[12:]}"
        return cnpj
    
    @staticmethod
    def format_phone(phone: str) -> str:
        """Formatar telefone"""
        if not phone:
            return ""
        
        digits = re.sub(r'\D', '', phone)
        if len(digits) == 11:
            return f"({digits[:2]}) {digits[2:7]}-{digits[7:]}"
        elif len(digits) == 10:
            return f"({digits[:2]}) {digits[2:6]}-{digits[6:]}"
        return phone
    
    @staticmethod
    def format_cep(cep: str) -> str:
        """Formatar CEP"""
        if not cep:
            return ""
        
        digits = re.sub(r'\D', '', cep)
        if len(digits) == 8:
            return f"{digits[:5]}-{digits[5:]}"
        return cep

# Instância global dos validadores
validators = DataValidators()