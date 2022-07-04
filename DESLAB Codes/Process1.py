## 1 Robot: Factory Process
## Events: 

from deslab import *

## ======================================================================================
## Cria os processos da máquina
def MachineProcess(machine,process):

    Mp = fsa()
    for p in process:
        I = 'I_{' + str(machine)+str(p)+'}'
        W = 'W_{' + str(machine)+str(p)+'}'
        start = 'start_{' + str(machine)+str(p)+'}'
        done = 'done_{' + str(machine)+str(p)+'}'

        X = [I, W]
        X0 = [I]
        Xm = [I]
        Sig = [start,done]
        T = [(I,start,W),(W,done,I)]

        M = fsa(X, Sig, T, X0, Xm)

        if isitempty(Mp):
            Mp = M
        else:
            Mp = parallel(Mp,M)

    Mp.name = '$M_{'+ str(machine)+'}$'
    
    return Mp

## ======================================================================================
## Cria of buffers da máquina
def MachineBuffers(machine,process):
    ## Fazendo Buffer de entrada:
    X_bi = list()

    Ei = 'Ei_{' + str(machine)+'}'
    X_bi.append(Ei)
    
    Sig_bi = list()
    T_bi = list()
    for p in process:
        Fi = 'Fi_{' + str(machine)+str(p)+'}'
        X_bi.append(Fi)
        In = 'in_{' + str(machine)+str(p)+'}'
        start = 'start_{' + str(machine)+str(p)+'}'
        Sig_bi.append(In)
        Sig_bi.append(start)
        T_bi.append((Ei,In,Fi))
        T_bi.append((Fi,start,Ei))

    X0_bi = [Ei]
    Xm_bi = [Ei]

    Bi = fsa(X_bi, Sig_bi, T_bi, X0_bi, Xm_bi)

    ## Fazendo Buffer de saída:

    X_bo = list()

    Eo = 'Eo_{' + str(machine)+'}'
    Fo = 'Fo_{' + str(machine)+'}'
    X_bo.append(Eo)
    X_bo.append(Fo)

    Sig_bo = list()
    T_bo = list()
    for p in process:
        out = 'out_{' + str(machine)+str(p)+'}'
        done = 'done_{' + str(machine)+str(p)+'}'
        Sig_bo.append(out)
        Sig_bo.append(done)
        T_bo.append((Eo,done,Fo))
        T_bo.append((Fo,out,Eo))
    
    X0_bo = [Eo]
    Xm_bo = [Eo]

    Bo = fsa(X_bo, Sig_bo, T_bo, X0_bo, Xm_bo)

    return [Bi,Bo]

## ======================================================================================
## Cria especificação necessaria para a
## maquina operar sem problemas.
def Spec(machine,process):
    Xs = list()
    X0 = '0'
    Xs.append(X0)

    Sigs = list()
    Ts = list()
    for p in process:
        X1 = '1'+str(p)
        X2 = '2'+str(p)
        Xs.append(X1)
        Xs.append(X2)

        start = 'start_{' + str(machine)+str(p)+'}'
        out = 'out_{' + str(machine)+str(p)+'}'
        done = 'done_{' + str(machine)+str(p)+'}'
        Sigs.append(start)
        Sigs.append(out)
        Sigs.append(done)

        Ts.append((X0,start,X1))
        Ts.append((X1,done,X2))
        Ts.append((X2,out,X0))

    S = fsa(Xs,Sigs,Ts,X0,X0)
    return S

## ======================================================================================
## Cria a maquina com as operações, buffers de entrada
## e saída e a especificação de funcionamento
def CreateMachine(machine,process):
    Mp = MachineProcess(machine,process)
    Bp = MachineBuffers(machine,process)
    Mspec = Spec(machine,process)
    Mpb = parallel(Bp[0],Mp)
    Mpb = parallel(Mpb,Bp[1])
    Mpbs = parallel(Mpb,Mspec)
    Mpbs.name = '$M_{'+ str(machine) +'}$'

    return Mpbs

## ======================================================================================
## Cria os armazens que entregam as matérias
## primas das peças para o robô.
## Parâmetro: (Si,[pn,...pm])
def CreateStorage(storage):
    X = list()
    T = list()
    Sigs = list()

    X0 = 'I_{'+str(storage[0])+'}'
    Xm = [X0]
    X.append(X0)
    for i in storage[1]:
        Xi = 'L_{'+str(storage[0])+str(i)+'}'
        X.append(Xi)
        rdy = 'rdy_{'+str(storage[0])+str(i)+'}'
        out = 'out_{'+str(storage[0])+str(i)+'}'
        Sigs.append(rdy)
        Sigs.append(out)
        T.append((X0,rdy,Xi))
        T.append((Xi,out,X0))

    Sto = fsa(X,Sigs,T,X0,Xm)
    Sto.name = '$Sto_{'+str(storage[0])+'}$'
    
    return Sto

## ======================================================================================
## Cria a esteira de saida que recebe as 
## peças finalizadas entregues pelo robô.
## Parâmetro: (CB,[pn,...,pm])
def CreateConveyorBelt(pecas):
    X = list()
    T = list()
    Sigs = list()

    X0 = 'I_{'+str(pecas[0])+'}'
    Xm = [X0]
    X.append(X0)
    for i in pecas[1]:
        Xi = 'U_{'+str(pecas[0])+str(i)+'}'
        X.append(Xi)
        rdy = 'rdy_{'+str(pecas[0])+str(i)+'}'
        In = 'in_{'+str(pecas[0])+str(i)+'}'
        Sigs.append(rdy)
        Sigs.append(In)
        T.append((X0,rdy,Xi))
        T.append((Xi,In,X0))

    Conv = fsa(X,Sigs,T,X0,Xm)
    Conv.name = '$Conv_{'+str(pecas[0])+'}$'
    
    return Conv

## ======================================================================================
## Cria as máquinas do processo inteiro de acordo com 
## as informações de armazéns, máquinas e esteira de saida.
def CreateProcessLine(storage,machines,conveyor):
    processLine = list()

    for i in range(len(storages)):
        Sto = CreateStorage(storages[i])
        processLine.append(Sto)
    
    for i in range(len(machines)):
        Mi = CreateMachine(machines[i][0],machines[i][1])
        processLine.append(Mi)

    Conv = CreateConveyorBelt(conveyor)
    processLine.append(Conv)
        
    return processLine

## ======================================================================================
def CreateTransport(storage,machines,conveyor):
    X = list()
    T = list()
    Sigs = list()
    
    X0 = 'E'
    Xm = X0
    X.append(X0)
    
    itens = storage
    itens.extend(machines)
    itens.append(conveyor)
    for i in itens[-1][1]:
        Xi = 'L_'+str(i)
        X.append(Xi)
        for j in itens:
            In = 'in_{'+str(j[0])+str(i)+'}'
            out = 'out_{'+str(j[0])+str(i)+'}'
            Sigs.append(In)
            Sigs.append(out)
            T.append((X0,out,Xi))
            T.append((Xi,In,X0))

    Trans = fsa(X,Sigs,T,X0,Xm,name = 'Transportation')
    return Trans

## ======================================================================================
## Cria os pontos de movimentação do robô pelo ambiente.
## Esses pontos são totalmente interligados.
## Parâmetro: quantidade de pontos disponíveis
def CreateMovement(places):
    X = list()
    T = list()
    Sigs = list()

    X0 = '0'
    Xm = X0

    for i in range(places):
        Xi = str(i)
        X.append(Xi)
        ito = 'm_{'+str(i)+'t'
        
        for j in range(places):
            Xj = str(j)
            if i!=j:
                itoj = ito + str(j)+'}'
                Sigs.append(itoj)
                T.append((Xi,itoj,Xj))

    Mov = fsa(X,Sigs,T,X0,Xm,name="Movement")
    
    return Mov

## ======================================================================================
## Maquinas do processo, definidas como um par ordenado de
## número da máquina x vetor de peças produzidas nela
## (Mi,[pn,...,pi])
machines = [(3,[1,2]),(4,[1,3]),(5,[1,3]),(6,[2]),(7,[2,3])]

## Armazens do processo, definidos como um par ordenado de
## número do armazem x vetor de materias brutas estocadas nele
## (Si,[pn,...pi])
storages = [(1,[1,2]),(2,[3])]
conveyor = (8,[1,2,3])

## Quantidade de localizações em que o robô pode se movimentar
## dentro da planta, sem considerar os múltiplos trajetos
locations = 9
