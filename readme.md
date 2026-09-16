# Roguenoid
Roguenoid é um jogo arcade desenvolvido em Python (Pygame) que mistura a clássica jogabilidade de destruição de blocos com mecânicas modernas de progressão no estilo Roguelike. 

Destrua os blocos, avance de nível e escolha upgrades para ficar cada vez mais forte. Se as suas vidas acabarem, não se preocupe: a pontuação e as fases são resetadas, mas **seus upgrades são mantidos** para a próxima tentativa!


## Pré-requisitos
Para executar este jogo, você precisará ter instalado em sua máquina:
- [Python 3.x](https://www.python.org/downloads/)
- Biblioteca `pygame`


## Como executar o jogo
1. Faça o download ou clone este repositório.
2. Abra o terminal (ou Prompt de Comando) e navegue até a pasta onde o arquivo do jogo está salvo.
3. Instale a biblioteca Pygame executando o comando abaixo:
   ```bash
   pip install pygame
Inicie o jogo executando o arquivo principal (supondo que o nome do arquivo seja roguenoid.py):

Bash
python roguenoid.py

## Controles
Seta para a Esquerda: Move a barra para a esquerda.

Seta para a Direita: Move a barra para a direita.

Teclas 1, 2 e 3: Selecionam o upgrade desejado ao final de cada nível.

Tecla R: Reinicia o jogo a partir da tela de Game Over.

Mecânicas Principais
Níveis de HP dos Blocos: Os blocos possuem cores diferentes baseadas em sua resistência (HP). Nas fases mais avançadas, blocos mais resistentes começarão a aparecer.

Física da Bola: A direção em que a bola rebate na barra depende de onde ela toca. Bater nas pontas da barra fará a bola ganhar um ângulo mais agudo.

Sistema Roguelike (Progressão Contínua): Ao finalizar um nível, o jogador escolhe 1 entre 3 upgrades aleatórios (Multibola, Mais Dano, Mais Vida, Barra Maior, Multiplicador de Pontos). Ao perder todas as vidas, o nível e os pontos resetam, mas a força e os upgrades acumulados pelo jogador permanecem para a próxima partida.