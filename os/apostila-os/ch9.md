# **Capítulo 9 — Interfaceamento e Drivers**

*“Se o kernel é o cérebro do sistema, os drivers são seus nervos e olhos: tudo o que o processador sabe sobre o mundo real passa através deles.” – em estilo Andrew S. Tanenbaum*

Drivers são o ponto onde o software encontra o hardware. Eles traduzem pulsos elétricos, registradores enigmáticos e sinais assíncronos em abstrações razoavelmente agradáveis para o programador. Ou, em termos mais realistas, tentam impedir que o caos natural do hardware vaze para as camadas superiores do sistema.

Ao longo deste capítulo, veremos não apenas como drivers são estruturados em sistemas embarcados, mas também como se comunicam com registradores, como lidam com interrupções e DMA, e quais princípios fazem a diferença entre um driver robusto e uma fonte de bugs que perseguirão desenvolvedores pela eternidade.

---

## **9.1 Estrutura de drivers em sistemas embarcados**

O conceito de *driver* varia de acordo com a complexidade do sistema. Em Linux, por exemplo, drivers são módulos sofisticados, integrados ao modelo de *device framework*. Em microcontroladores simples, um driver pode ser apenas um conjunto de funções que leem e escrevem registradores.

Apesar dessas diferenças, três princípios fundamentais aparecem em quase todos os drivers embarcados:

1. **Inicialização do periférico**
   Configurar clocks, habilitar GPIOs, setar registradores.
2. **Operação**
   Ler/escrever dados, iniciar transações, esperar eventos.
3. **Interrupções/Callbacks**
   Reagir a eventos assíncronos.
4. **Encerramento ou reset**
   Quando necessário (em sistemas embarcados, muitas vezes é opcional).

### **Um exemplo minimalista de driver: GPIO no ARM Cortex-M**

Esse exemplo representa o estilo comum de drivers em plataformas STM32:

```c
// Arquivo: gpio.h
void gpio_init_output(void);
void gpio_set(int value);

// Arquivo: gpio.c
#include <stdint.h>

#define RCC_AHB2ENR   (*(volatile uint32_t*)0x4002104C)
#define GPIOA_MODER   (*(volatile uint32_t*)0x48000000)
#define GPIOA_ODR     (*(volatile uint32_t*)0x48000014)

void gpio_init_output() {
    RCC_AHB2ENR |= (1 << 0);       // habilita clock do GPIOA
    GPIOA_MODER &= ~(3 << (5*2));  // limpa bits
    GPIOA_MODER |=  (1 << (5*2));  // PA5 como saída
}

void gpio_set(int value) {
    if (value)
        GPIOA_ODR |=  (1 << 5);
    else
        GPIOA_ODR &= ~(1 << 5);
}
```

Aqui já vemos características típicas:

* registradores mapeados em memória
* manipulação bit a bit
* inicialização separada da operação

Este é o nível fundamental: todo driver sofisticado começa assim.

---

## **9.2 Comunicação com periféricos via registradores**

Hardware embarcado raramente opera via chamadas de função — ele expõe **registradores**. Um driver nada mais é do que um tradutor entre esses registradores e a aplicação.

#### **Registradores mapeados em memória**

Os microcontroladores expõem registradores como endereços fixos, seguindo a técnica de *memory-mapped I/O*.

Exemplo didático: leitura do status de um UART (ARM Cortex-M).

```c
#define USART2_SR   (*(volatile uint32_t*)0x40004400)
#define USART2_DR   (*(volatile uint32_t*)0x40004404)

int uart_read_byte(void) {
    while (!(USART2_SR & (1 << 5))) {
        // espera até RXNE (Receive Not Empty)
    }
    return USART2_DR & 0xFF;
}
```

Note a palavra-chave **volatile**: sem ela, o compilador poderia remover ou reordenar leituras, resultando em comportamento incorreto, pois os registradores mudam “por conta própria”.

#### **Campos de bits**

Registradores costumam ter múltiplas funções em um único inteiro. Por exemplo, o registrador SPI_CR1 de um STM32:

```c
#define SPI_CR1_CPOL   (1 << 1)
#define SPI_CR1_MSTR   (1 << 2)
#define SPI_CR1_BR(x)  ((x) << 3)
```

Manipular isso exige cuidado, e uma prática comum é definir máscaras e constantes para evitar valores mágicos.

#### **Sequências obrigatórias**

Alguns periféricos **exigem** ordem específica:

1. Habilitar clock
2. Reset
3. Configurar modo
4. Habilitar periférico

Um exemplo real (I2C STM32, simplificado):

```c
I2C1->CR1 &= ~I2C_CR1_PE;      // desabilita I2C
I2C1->CR2 = config->freq;
I2C1->CCR = config->clock_control;
I2C1->TRISE = config->rise_time;
I2C1->CR1 |= I2C_CR1_PE;       // habilita I2C
```

Não seguir a ordem pode travar o barramento — um clássico para quem já depurou I2C às 3 da manhã.

---

## **9.3 Drivers síncronos e assíncronos**

#### **O driver síncrono**

Bloqueia até terminar a operação.
Simples, previsível — mas pode bloquear o sistema.

Exemplo de leitura síncrona em SPI:

```c
uint8_t spi_transfer(uint8_t data) {
    SPI1->DR = data;
    while (!(SPI1->SR & (1 << 0))); // espera RXNE
    return SPI1->DR;
}
```

Código ótimo para um sistema simples, mas problemático se o periférico for lento. Em um RTOS, bloquear a CPU pode fazer outras tarefas perderem deadlines.

#### **O driver assíncrono**

A operação é iniciada e o término é sinalizado por:

* interrupção
* callback
* evento RTOS
* DMA

Exemplo: transferência UART com interrupção (pseudocódigo simplificado):

```c
void uart_send_async(uint8_t b) {
    USART2_DR = b;
    USART2_CR1 |= (1 << 7);  // habilita TXE interrupt
}

void USART2_IRQHandler(void) {
    if (USART2_SR & (1 << 7)) {  // TXE flag
        // envia próximo byte...
    }
}
```

O fluxo é mais complexo, mas evita bloqueios.

#### **Qual escolher?**

| Critério     | Síncrono              | Assíncrono                 |
| ------------ | --------------------- | -------------------------- |
| Simplicidade | Alta                  | Baixa                      |
| Latência     | Alta                  | Baixa                      |
| Uso de CPU   | Ruim                  | Excelente                  |
| Determinismo | Alto (mas bloqueante) | Alto (com ISR bem escrita) |
| Throughput   | Limitado              | Alto                       |

Em sistemas modernos, drivers assíncronos são preferidos para quase tudo.

---

## **9.4 Interrupções e DMA**

Drivers reais raramente fazem tudo por CPU. Dois mecanismos poderosos ajudam enormemente:

---

### **Interrupções**

A ISR sinaliza eventos de hardware, como:

* byte recebido
* buffer transmitido
* erro no periférico
* timer expirado

Exemplo típico de ISR UART (ARM Cortex-M, simplificado):

```c
void USART2_IRQHandler(void) {
    if (USART2_SR & (1 << 5)) {  // RXNE
        uint8_t b = USART2_DR;
        ringbuffer_put(b);
    }
}
```

A ISR deve ser curta e objetiva: qualquer processamento pesado deve ser **deferido** para uma tarefa do RTOS.

---

#### **DMA (Direct Memory Access)**

DMA libera a CPU ao permitir que o periférico copie dados diretamente da memória.

Perfeito para:

* áudio
* vídeo
* pacotes de rede
* buffers grandes de UART/SPI
* sensores de alta taxa

Exemplo: SPI usando DMA para transmitir um buffer:

```c
DMA1_Channel3->CMAR = (uint32_t)buffer;
DMA1_Channel3->CNDTR = length;
DMA1_Channel3->CCR |= DMA_CCR_EN;

SPI1->CR2 |= SPI_CR2_TXDMAEN;
```

Quando a transferência termina, o DMA dispara uma interrupção — o driver só precisa processar o *callback*.

#### **Vantagens do DMA**

* reduz uso de CPU
* permite taxas muito altas
* reduz jitter
* permite paralelismo real

#### **Armadilhas do DMA**

* buffers precisam ser contíguos
* alinhamento pode importar
* interferência com cache (em SoCs)
* difícil depurar
* requer tratamento cuidadoso de eventos de término

Em microcontroladores modernos, drivers de alto desempenho são quase sempre baseados em DMA.

---

## **9.5 Boas práticas de desenvolvimento de drivers**

#### **1. Nunca confie no hardware. Verifique tudo.**

Erratas de microcontroladores existem — mais do que gostaríamos.
Um bit que deveria ser limpo automaticamente talvez não o seja.
Um flag pode precisar ser escrito duas vezes.

#### **2. Mantenha ISR mínima e objetiva**

Regra de ouro:

> *“ISR curta. Sempre.”*

Longas ISRs podem gerar jitter, travar escalonamento e bagunçar temporização de tempo real.

#### **3. Use abstrações claras**

Um bom driver expõe:

* funções simples
* sem detalhes de registradores
* sem valores mágicos
* sem expor estados internos indevidos

#### **4. Separe camadas**

Estrutura ideal em embarcados:

```
App → HAL (API amigável) → Driver → Registradores
```

#### **5. Evite bloqueios desnecessários**

Se possível:

* use interrupções
* use DMA
* use RTOS signals/queues

#### **6. Documente cada bit manipulado**

Nada envelhece pior do que driver mal documentado.
Comentários como:

```c
// Clear OVR bit to resume operation (see Errata §3.2.4)
```

salvam vidas.

#### **7. Teste com hardware real e com simulação**

Testes de unidade podem falhar em simular:

* glitches elétricos
* tempo de setup/hold real
* clock drifting

Ambos são necessários.

