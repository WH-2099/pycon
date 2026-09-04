---
conversion: "PDF converted with pdftotext -layout; page layout, code, and equations may be imperfect."
retrieved: "2026-09-04"
source: "https://drops.dagstuhl.de/storage/00lipics/lipics-vol391-concur2026/LIPIcs.CONCUR.2026.23/LIPIcs.CONCUR.2026.23.pdf"
title: "When Behaviours Have to Happen: An Axiomatic Model of Causality in Behaviour-Oriented Concurrency"
---

<!-- rumdl-disable-file -->

when Behaviours Have to Happen
An Axiomatic Model of Causality in Behaviour-Oriented Concurrency
Luke Cheeseman #
Uppsala University, Sweden
Elias Castegren #
Uppsala University, Sweden
Tobias Wrigstad #
Uppsala University, Sweden
Sophia Drossopoulou #
Imperial College London, UK
Matthew J. Parkinson #
Azure Research, London, UK

      Abstract
Behaviour-oriented concurrency (BoC) is a recently established programming model in which
programmers define concurrent operations that execute atomically across multiple isolated resources.
This allows for expressive interactions but introduces complex causal dependencies determined by
dynamic resource overlap. Previous work defines the causal guarantees of BoC operationally, but
mixes intended design constraints with incidental implementation details, leading to unintended
causal orders. BoC is now being implemented across multiple languages and runtimes, all relying on
the operational descriptions of causality. This paper develops an axiomatic model of BoC executions
that makes the intrinsic orders explicit and derives the intended causal relation from their interaction.
Using a set of representative programs and candidate executions, we motivate the design of this
causal relation. We then prove that a representative minimal core calculus for BoC is sound with
respect to this axiomatic model. Together, these results provide an implementation-independent
foundation for reasoning about BoC causality across runtimes, schedulers and optimisation decisions.

2012 ACM Subject Classification Theory of computation → Concurrency

Keywords and phrases Concurrency, Parallelism, Language Design, Causality

Digital Object Identifier 10.4230/LIPIcs.CONCUR.2026.23

Supplementary Material Software (Proofs): https://github.com/fxpl/axiomatic_boc [7]
   archived at swh:1:dir:24350cf7167ab1b9d00f8a2d64cc3fe32dfb4560

Acknowledgements We thank David Black-Schaffer and the reviewers for helpful discussions and
feedback on the paper.


 1      Introduction
Modern concurrent programming must balance the efficiency benefits of parallelism against
the complexity of reasoning about program execution. Behaviour-oriented concurrency (BoC)
is a programming model in which tasks declare required isolated resources; tasks with disjoint
requirements may execute concurrently, while tasks with overlapping requirements are subject
to explicit ordering guarantees, simplifying reasoning about program execution [10]. Previous
work on BoC defines these ordering guarantees operationally, but mixes intended design
constraints with incidental implementation details, inducing unintended causal orders [10].
BoC is now being developed in multiple languages and runtimes, including C++ and Python
runtimes, and research languages such as Verona [22, 12, 13, 4]. As these efforts evolve, they
rely on the informal and overly restrictive descriptions of causality inherent in the operational
            © Luke Cheeseman, Elias Castegren, Tobias Wrigstad, Sophia Drossopoulou, and Matthew J.
            Parkinson;
            licensed under Creative Commons License CC-BY 4.0
37th International Conference on Concurrency Theory (CONCUR 2026).
Editors: Ana Sokolova and Patrick Totzke; Article No. 23; pp. 23:1–23:17
                   Leibniz International Proceedings in Informatics
                   Schloss Dagstuhl – Leibniz-Zentrum für Informatik, Dagstuhl Publishing, Germany
23:2   when Behaviours Have to Happen


        1       def main(src: cown[Account], dst: cown[Account]) {
        2        when(src) { A src.balance += 10; }
        3        when(dst) { B dst.frozen = true; }
        4        when(src, dst) { C
        5          if (!dst.frozen && !src.frozen && src.balance >= 10) {
        6           src.balance -= 10;
        7           dst.balance += 10;
        8       } } }


                Figure 1 Bank account operations using cowns and behaviours.

                                     Initially, both src and dst have balance 0.
       (a) Update path (src then dst).                     (b) Diagnostic path (dst then src).
            1    when(src){   D   src.balance += 10; }       1   when(dst){    F   print(dst.balance); }
            2    when(dst){   E   dst.balance += 10; }       2   when(src){    G   print(src.balance); }


                Figure 2 Independent concurrent behaviours with unintended induced causality.



       semantics. This impedes the development of optimisations and tooling, and makes it difficult
       to reason about the intended causal guarantees of BoC across implementations. In this
       paper, we introduce an implementation-agnostic axiomatic account of BoC that captures the
       intrinsic orders as well as the intended causal order.
           In BoC, an isolated resource is called a cown (pronounced “cone”) and the concurrent
       tasks are called behaviours. Figure 1 shows an example of BoC where cowns src and dst
       each own a unique bank account and behaviours perform asynchronous atomic tasks over
       accounts. The keyword when denotes spawning a behaviour which requires the declared cown
       set. The behaviours will execute asynchronously once all previously spawned behaviours that
       require overlapping cowns have completed (and thus the cowns are available). Behaviour
        A deposits money into the source account, behaviour B freezes the destination account

       (making future operations on it unavailable), and behaviour C performs a transfer from the
       source to the destination account if neither is frozen and the source has sufficient balance.
       The intention of this program is that the deposit and freeze behaviours ( A and B ) always
       occur before the transfer behaviour ( C ) (thus observing the effects of the deposit and freeze),
       while the deposit and freeze behaviours may proceed concurrently. This example relies on
       the causal order guaranteed by BoC to ensure that these intentions are met: because the
       transfer behaviour is spawned after the deposit and freeze behaviours, it will only execute
       after they have completed, and thus will see their effects.
           Figure 2 illustrates a different example in BoC, where the intended behaviour is that
       the update and diagnostic paths are independent and their behaviours can execute in any
       order. However, the operational semantics for BoC, presented in earlier work [10], induces
       an undesirable causal order between the two paths, which is more restrictive than intended.
       In the operational semantics, it is not possible to have both G execute before D and E
       execute before F , which would print src = 0 and dst = 10. This outcome stems from the
       structures and relations defined in the operational semantics, which are not intrinsic to the
       BoC model but rather reflect a particular implementation strategy.
           In order to separate intrinsic causal guarantees from implementation artefacts, we will
       define causality in BoC using an axiomatic model. Our model follows the event-and-relation
       methodology used in modern weak-memory axiomatic frameworks [2], but instantiates it
       with the lifecycle events of behaviours and their dynamic ordering. We introduce the model
L. Cheeseman, E. Castegren, T. Wrigstad, S. Drossopoulou, and M. J. Parkinson                                 23:3


   Table 1 Sequential executions for Figure 2, grouped by printed output. In the status row, ✓
denotes desirable and permitted under the operational semantics; ▲ denotes desirable but excluded.

                   src=0, dst=0         src=0, dst=10           src=10, dst=0         src=10, dst=10

                    F   E       G   D       E   F       G   D    D    F       E   G     D   E       F   G

                    F   G       D   E       E   G       D   F    D    F       G   E     D   E       G   F

                    F   G       E   D       E   G       F   D    D    G       F   E     D   G       E   F
          Order
                    G   D       F   E       G   D       E   F     F   D       E   G     E   D       F   G

                    G   F       D   E       G   E       D   F     F   D       G   E     E   D       G   F

                    G   F       E   D       G   E       F   D     F   E       D   G     E   F       D   G


          Status            ✓                       ▲                     ✓                     ✓


through a series of example programs and their candidate executions. We then demonstrate
that a minimal core calculus, inspired by the prior operational semantics, is sound with
respect to this axiomatic model. This establishes the axiomatic model as a foundation for
reasoning about BoC causality across runtimes, schedulers and optimisation decisions.

Contributions
     An informal characterisation of the intended BoC ordering constraints (Section 2).
     An axiomatic model for BoC capturing these constraints precisely (Section 3).
     A representative minimal core calculus for BoC, together with a mechanised Lean proof
     that its executions are sound with respect to the axiomatic model (Section 4).
     An analysis of the practical utility of the axiomatic model for reasoning about tooling,
     optimisation, and program transformations (Section 5).


 2      An informal description of causality
In earlier work, we provided an informal definition of the happens-before guarantee in the
operational semantics for BoC [10]. It is reproduced in Definition 1.

▶ Definition 1 (Restrictive informal happens-before). A behaviour b will happen before another
behaviour b′ iff b and b′ require overlapping sets of cowns, and b is spawned before b′ .

This definition restricts behaviours to happen before each other based on their spawning
order, which may just be an artefact of an execution, rather than an intrinsic property of the
program. Under this definition, we get the desired ordering of behaviours in Figure 1, but
we also get the unintended ordering in Figure 2. Table 1 presents the possible interleavings
of behaviours for the program in Figure 2 and whether the order is a permissible execution.
Only 16 of the 24 possible orders are permissible, and all of the permissible orders have either
 D happen before G or F happen before E . We summarise this as Observation 2:


▶ Observation 2. In Figure 2            D   happens-before G ∨ F happens-before                 E


In every execution, D will be spawned before E and F before G , reflecting the program
order. Now, assume that we want to print src = 0. It must be that G is spawned before D .
This means in such an execution, transitively, F will be spawned before E , and thus we
will always see dst = 0 for the restrictive definition of happens-before.




                                                                                                            CONCUR 2026
23:4   when Behaviours Have to Happen


       (a) Apply and log account update.                                   (b) Deposit money.
        1    def update(account: cown[Account], amount: int) {               1   update(a, +100)
        2     when(account) { H
        3       if (account.balance + amount >= 0) {
        4         account.balance += amount                                (c) Withdraw money.
        5         val id = account.id                                        1   update(a, -100)
        6         when(log) { I
        7          log.record(id, amount)
        8    } } } }


            Figure 3 Independent concurrent behaviours with intended induced causality.

           Table 2 Sequential executions for Figure 3, grouped by update and logging order (+ behaviours
       corresponds to deposit, − to withdraw). ✓ desirable and permitted; ✗ undesirable and excluded.

                     upd(+-), log(+-)      upd(+-), log(-+)   upd(-+), log(+-)    upd(-+), log(-+)

                      H + I + H − I −      H + H − I − I +    H − H + I + I −      H − H + I − I +
             Order
                      H + H − I + I −                                              H − I − H + I +


            Status           ✓                    ✗                    ✗                    ✓


           Now consider Figure 3, where the restrictive order provides the desired guarantees for
       a program. The update method uses nested when blocks to access the account, determine
       whether the update is valid, and then log the update. The recorded log can then be used for
       auditing or rebuilding the state of the account.
           Two independent concurrent updates are shown on the right of Figure 3, one to deposit
       money and one to withdraw money. Accounts cannot be withdrawn from if they do not have
       sufficient balance, and such operations will be rejected (Line 3). For example, with an initial
       balance of 0, if the deposit is applied first, then the final balance after the withdrawal will be
       0; whereas, if the withdraw update is applied first, then the final balance after the deposit
       will be 100. This means the order that these updates are applied will affect the final state of
       the account, and we want that whichever update is applied first must also be logged first to
       ensure the log is correct and useable.
           Table 2 shows the possible interleavings of the program in Figure 3, whether they are
       possible under the operational semantics, and whether this is desirable. We denote the
       deposit, update and log behaviours using a “+” suffix, and the withdraw behaviours using
       a “−” suffix. In this instance, the desirable and permitted executions are the same, and
       the undesirable and excluded executions are the same. As summarised by Observation 3,
       whichever update is applied first will also be logged first.

       ▶ Observation 3.

             In Figure 3 ( H + happens-before H − ⇐⇒            I   + happens-before   I   −)
                       ∧ ( H − happens-before H + ⇐⇒            I   − happens-before   I   +)

           These examples demonstrate that whilst the operational semantics for BoC captures some
       of the intended causal order, it does not capture all of it. It is also more restrictive than it
       needs to be. We could modify the operational semantics to permit the desired executions in
       Figure 2, but this would complicate the semantics. Instead, in the next section we abstract
       away from the operational semantics and define the intended causal orders in terms of the
       intrinsic orders of the programming model.
L. Cheeseman, E. Castegren, T. Wrigstad, S. Drossopoulou, and M. J. Parkinson                        23:5


 3     An Axiomatic Model of Causality in BoC

We now use the intuition of causality from the previous section to construct an axiomatic
model of BoC executions and judge whether candidate executions are valid or invalid. In
particular, we define the structure of events and relations that form the model, and then
define axioms on these relations that determine which executions are valid. This includes
defining the more precise happens-before relation that permits the desired executions for our
motivating examples in Figure 2 and Figure 3.


3.1    Candidate Executions
Candidate executions represent the possible sequences of events in a BoC program.

▶ Definition 4 (Structure of BoC executions). Assuming two sets BId and CId of behaviour
and cown identifiers respectively, a candidate execution is a tuple (E, po, co):

(1) Spawn ⊆ {Si | i ∈ BId}                          (4) E = Spawn ∪ Run ∪ Complete
(2) Run ⊆ {Ri | i ∈ BId}                            (5) co ⊆ (CId × Complete × Run)
(3) Complete ⊆ {Ci | i ∈ BId}
(6) po ⊆ (Run × Spawn) ∪ (Run × Complete) ∪ (Spawn × Spawn) ∪ (Spawn × Complete)

Definition 4 defines the structure of a candidate execution, including the events and relations.
A candidate execution is a tuple of a set of events E, a program order relation po, and a cown
order relation co. There are three types of events: spawn events, start events, and completion
events. These events are self explanatory, with the subscript indicating the behaviour they
relate to. The program order (po) relation captures the static order in which a behaviour
starts, spawns subsequent behaviours, and completes. The cown order (co) captures the
dynamic order in which behaviours using the same cowns complete and start. We do not
define the cowns that are used in an execution directly; this information is attached to the
order of events in the cown order. This structure assumes that all behaviours have unique
identifiers, and that the events of a behaviour are uniquely identified by the behaviour’s
identifier and the type of event.
    For the remainder of this section, we fix an execution (E, po, co). All derived relations
and functions are defined relative to this fixed execution.

▶ Definition 5 (Derived relations). The following relations are derived:
(1) r = {(Si , Ri ) | Si ∈ E, Ri ∈ E}
(2) coc = {(Ci , Rj ) | (c, Ci , Rj ) ∈co }
          S
(3) co∗ = c∈CId coc

In Definition 5 we derive three additional relations from the structure of candidate executions:
spawn-run order (r), a cown-specific cown order (coc ), and an global cown order (co∗ ). The
second relation projects the cown order onto specific cowns, allowing us to determine the
order of events that use the same cowns. The third relation aggregates the cown-specific
orders into a single global order, capturing the overall ordering of events across all cowns.
    Let us take the example in Figure 3 and illustrate the structure of the candidate execution
and the derived relations. We will take an execution where H + happens-before H − and
thus I + happens-before I −. This execution is illustrated in Figure 4, where the events
are ordered from left to right, and the relations are shown as labelled arrows between events.



                                                                                                   CONCUR 2026
23:6   when Behaviours Have to Happen


                                                                r

                           r             po            po                           po
                  SH+           RH+            SI+          CH+            RI+           CI+
                                              coa
                                                                r
                                                                                      colog

                  SH−           RH−            SI−          CH−            RI−            CI−
                           r             po            po                           po


          Figure 4 A valid execution of the program in Figure 3, with the events and relations illustrated.


       3.2     Deriving Happens-before
       We now have the intrinsic events and relations of a BoC execution that enable us to precisely
       define the intended causal ordering constraints.

       ▶ Definition 6 (Cowns). We define the function cowns : BId → P(CId), which maps a
       behaviour identifier to the set of cowns that behaviour uses, as follows:

          cowns(i) = {c | (c, _, Ri ) ∈co ∨ (c, Ci , _) ∈co }

       ▶ Definition 7 (Happens-before). We use the notation _+ to denote the transitive closure of
       a relation. Happens-before is defined as the relation hb ⊆ Complete × Run such that:

          hb   = {(Ci , Rj ) | Si (po ∪ r ∪ co)+ Sj ∧ cowns(i) ∩ cowns(j) ̸= ∅ ∧ {Ci , Rj } ⊆ E}

       Definition 7 captures the happens-before guarantees which satisfy the intended causal
       ordering for our motivating examples. For a given complete event Ci and run event Rj , we
       can determine whether Ci happens-before Rj by finding the spawn events Si and Sj that
       correspond to Ci and Rj , then traversing the program order, cown order, and spawn-run
       order relations to determine whether Si is causally before Sj . This states that if behaviour
       i is causally, and not incidentally, spawned before behaviour j, and they use overlapping
       cowns, then the completion of behaviour i happens-before the run of behaviour j.

       3.3     Axioms for Valid Candidate Executions
       We want all executions which are well-formed, and whose event orders respect the happens-
       before orders, to be valid executions. In the execution in Figure 4, we can see that C I +
       happens-before R I − , since S I + po C H + coa R H − po S I − , and cowns( I +)∩cowns( I −) =
       {log}. If we add the happens-before edges to the execution in Figure 4, presented in Figure 5a,
       we can see that the happens-before edges are consistent with cown order of the execution.
       Thus, this is a valid execution.
           Invalid executions are those where the intended happens-before guarantees are not
       respected. One such execution is a variant of the execution in Figure 4 where C I − colog R I +
       instead of C I + colog R I − , which would correspond to the withdrawal being applied before
       the deposit but the log recording the deposit before the withdrawal. This is presented in
       Figure 5b, where the events and relations are the same as in Figure 4 except for the cown
       order between C I + and R I − . We also include the derived happens-before relation, which
       includes the intended happens-before between C I + and R I − .
           To judge whether an execution is valid or invalid we use the axioms of the axiomatic
       model, which define the constraints that a valid execution must satisfy.
L. Cheeseman, E. Castegren, T. Wrigstad, S. Drossopoulou, and M. J. Parkinson                                   23:7


                                         r                                         r

        r           po              po                     po                                  po
 SH+        RH+            SI+           CH+     RI+             CI+                   RI+          CI+
                         coa
                                                      hb
                               hb        r                                         r      hb        colog
                                                                colog

 SH−        RH−            SI−           CH−     RI−             CI−                   RI−          CI−
        r           po              po                     po                                  po

(a) A valid execution.                                                       (b) An invalid execution (log
                                                                             order violation).

   Figure 5 Two candidate executions of the program in Figure 3.



▶ Definition 8 (Valid execution). An execution (E, po, co) is valid if it satisfies the following
constraints:
(1) ∀e1 , e2 . e1 po e2 ∨ e1 co e2 =⇒ {e1 , e2 } ⊆ E Relations only relate events in the execution
(2) ∀e ∈ E . ∃i . Ri po∗ e                                      Every event has a corresponding run event
(3) ∀Ri ∈ E . Cj ∈ E . Ri po∗ Cj =⇒ i = j                           Corresponding run and complete events
(4) ∀e1 , e2 , e3 ∈ E . e1 po e3 ∧ e2 po e3 =⇒ e1 = e2                    Unique ancestors in program order
(5) ∀e1 , e2 , e3 ∈ E . e1 po e2 ∧ e1 po e3 =⇒ e2 = e3                  Unique descendants in program order
(6) ∀e1 , e2 , e3 ∈ E, c . e1 coc e3 ∧ e2 coc e3 =⇒ e1 = e2                  Unique ancestors in cown order
(7) ∀e1 , e2 , e3 ∈ E, c . e1 coc e2 ∧ e1 coc e3 =⇒ e2 = e3               Unique descendants in cown order
(8) ∀e1 , e2 , e3 , e4 ∈ E, c . e1 coc e2 ∧ e3 coc e4 ∧ e1 ̸= e3 =⇒ e2 (po ∪ coc )∗ e3 ∨ e4 (po ∪ coc )∗ e1
                                                                             Cown order forms a single path
                                             +
(9) ∀e1 , e2 ∈ E . e1 (po ∪ co∗ ∪ r ∪ hb) e2 =⇒ e1 ̸= e2                                 Causal consistency


Items 1–8 are sanity constraints on the structure of executions, ensuring that the relations
only relate events in the execution (1), that every event has a corresponding run event (2),
that a run event corresponds to the complete event of the same behaviour (3), that the
relations do not form a branching structure (4–7), and that the cown order (together with
program order) forms a single linear path (8). The final constraint, 9, ensures that the
execution is causally consistent; this is achieved by ensuring the transitive closure of the
union of the relations, including the happens-before relation, is acyclic. Note that we do not
require a constraint that all run events have a corresponding spawn event; such a constraint
paired with 2 would require an infinite chain of events (or a cycle precluded by 9).
    We can now judge both that the execution in Figure 5a is valid, and that the execution
in Figure 5b is invalid. The execution in Figure 5a is valid because it satisfies all of the
constraints in Definition 8, including the final constraint of causal consistency, since there
are no cycles in the union of the relations. The execution in Figure 5b is invalid, since the
happens-before relation between C I + and R I − forms a cycle, which violates the causal
consistency constraint (item 9).
    Moreover, all of the executions in the earlier Table 1 are valid under Definition 8, including
those excluded by the operational semantics. Figure 6a presents one such valid execution,
excluded by the operational semantics, where E runs and completes before F , and G runs
and completes before D . There is a deliberate and desired absence of happens-before edges,
since no behaviour is causally before any other. In fact, no matter which order the behaviours
run and complete, there would be no derived happens-before edges; there is no causal path
from the spawn of one behaviour to the spawn of another that uses the same cowns.



                                                                                                              CONCUR 2026
23:8   when Behaviours Have to Happen


                  r        po                po         r                        r           po                       po          r
       SD             RD        CD      CF         RF       SF             SD        RD           CD           CF          RF          SF

             po                                              po             po                                                            po
                           cosrc           codst                                      hbos         codst      cosrc        hbos

       SE             RE        CE      CG         RG       SG             SE        RE           CE           CG          RG          SG
                  r        po                po         r                        r           po                       po          r

       (a) Definition 7 does not induce any happens-before             (b) The operational semantics happens-before, from
       relations from the candidate execution.                         Definition 9, induces a cycle.

             Figure 6 A valid execution which cannot happen in the operational semantics.

                                                                                                          r
                                                                       r             po           po                         po
                                                             SJ            RJ             SK           CJ             RK          CK
         1    when(src) { J                                                           hb
         2     when(log) { K }                                    po
         3    };                                                                                   cosrc
                                                                       r                     po
         4    when(src, dst) { L };                          SL            RL                          CL                  hb
                                                                                     hb
         5    when(dst) { M                                                                                                           colog
                                                                  po
         6     when(log) { N }                                                                    codst
         7    };
                                                             SM            RM             SN           CM             RN          CN
                                                                       r             po           po                         po
                                                                                                          r


             Figure 7 Leap-frogging causality from program order, transitive dependencies, and nesting.


       3.4            Causality Through Transitivity
       The happens-before relation can also leap-frog over program order, transitive dependencies,
       and nesting. This is an important result as it shows that the happens-before relation can
       capture orderings between behaviours whose parents do not use the same cowns. In Figure 7,
       we have a program where J and M are directly linked only by program order, but are
       indirectly linked by the intermediate behaviour L , which uses the same cowns as J and M .
       This means that the completion of J happens-before the run of M , creating a subsequent
       happens-before relation from the run of K to the run of N . This is illustrated in the
       execution on the right of Figure 7.

       3.5            Capturing the Operational Semantics Happens-before
       We can also capture the happens-before relation that would make the operational semantics
       complete with respect to the axiomatic model. In Definition 9, the happens-before relation
       acts to retroactively order the spawn events of behaviours based on the cown order of their
       completion and run events:

       ▶ Definition 9 (Operational Semantics Happens-before). If a behaviour i completes before a
       behaviour j runs and they use overlapping cowns, then it must have been that behaviour i
       was spawned before behaviour j.

             hbos      = {(Si , Sj ) | Ci co∗ Rj }

       We illustrate the happens-before relation under the operational semantics definition, in
       Definition 9, in Figure 6b. Under this definition, the happens-before relation retroactively
       orders the spawn events of behaviours based on the cown order of their completion and run
       events, which induces ordering constraints between the behaviours that are not intended by
L. Cheeseman, E. Castegren, T. Wrigstad, S. Drossopoulou, and M. J. Parkinson                               23:9



             i ∈     BId          e ∈     Event = { Si , Ri , Ci | i ∈ BId }
             c ∈     CId         H ∈      History = (BId → Event) × (CId → Event)

                          s ::= when(c){s}; s | done (Statements)
                          b ::= (i, c, s)            (Behaviours)
                        cfg ::= ⟨b, b⟩               (Configuration)


     Figure 8 Syntax of histories and the core BoC calculus. We use x for zero or more x’s in sequence.


the programmer. In particular, we can see that C G cosrc R D induces a happens-before edge
from S G to S D , and C E codst R F induces a happens-before edge from S E to S F . This
forms a cycle in the relations of the execution, which would violate the causal consistency
constraint and would make the execution invalid.


 4      Connecting the Axiomatic and Operational Models of BoC
In this section we define a core calculus describing BoC. It is similar to a previous calculus for
BoC [10], but differs in that it has a concrete (albeit minimal) sequential language and that
it produces a log of events. We relate the core calculus to the axiomatic model and prove
that every execution is valid. All definitions and proofs (modulo notational conveniences)
have been been mechanised in the Lean theorem prover [7].

4.1      Syntax and Semantics of a Core BoC Calculus
Figure 8 shows the syntax of histories and our core calculus. A history H maps behaviour
identifiers i and cown identifiers c to sequences of events. Through slight abuse of notation, we
write H(i) and H(c) for looking up the event sequences of behaviours and cowns respectively.
Events are defined as the Spawn (S), Run (R) or Complete (C) events of some behaviour, as
in the previous section. The intuition is that H(i) contains the history of events caused by
behaviour i, while H(c) contains run and completion events of behaviours that require cown
c. A history is total and initially maps behaviours and cowns to empty sequences.
    A statement s is a sequence of when blocks, each of which lists its required cowns and the
statement to be run. A behaviour b has an identifier, a set of required cowns and its current
statement. A configuration cfg consists of a collection of currently running behaviours and a
queue of spawned but not yet running behaviours. In the semantics we use br and bp for
the collections of running and pending behaviours respectively. We write br [(i, c, s)] for a
collection b′r : (i, c, s) : b′′r , allowing us to focus on a single behaviour in a collection. We use
the shorthands H[i += e] and H[c += e] to append an event e to the history of a behaviour or
a set of cown histories respectively.
    Figure 9 shows the small-step semantics of our core calculus. The sequential part of
the calculus has a single rule Step which executes the next when block, emitting a tuple
of its required cowns c and internal statement s1 . The remaining three rules describe the
concurrent semantics of the calculus. They each take the shape cfg/H ⇝ cfg ′ /H ′ , performing
some scheduling action on cfg and extending the history H with the corresponding event.
    The Spawn rule non-deterministically picks a running behaviour and executes its next
when block (via the Step rule). A new behaviour with a fresh identifier j and the emitted
cowns and statement are appended to the end of the queue of pending behaviours. The



                                                                                                          CONCUR 2026
23:10   when Behaviours Have to Happen




                                                                                    Step
                                         when(c){s1 }; s2 ,→ s2 | (c, s1 )

                                        s1 ,→ s2 | (c3 , s3 )          j fresh
                                                                                                           Spawn
                  ⟨br [(i, c1 , s1 )], bp ⟩ / H ⇝ ⟨br [(i, c1 , s2 )], bp : (j, c3 , s3 )⟩ / H[i += Sj ]

                           C = {c | c ∈ c′ ∧ (_, c′ , _) ∈ br ∪ bp1 }                C ∩c=∅
                                                                                                              Run
               ⟨br , bp1 : (i, c, s) : bp2 ⟩ / H ⇝ ⟨br : (i, c, s), bp1 : bp2 ⟩ / H[i += Ri ][c += Ri ]


                                                                                                 Complete
                    ⟨br [(i, c, done)], bp ⟩ / H ⇝ ⟨br [ϵ], bp ⟩ / H[i += Ci ][c += Ci ]


           Figure 9 Semantics of the core BoC calculus with histories.



                                     WFB-Empty                                     WFB-NEmpty
                            i ⊢b ϵ                        i ⊢b Ri : S : (Ci ?)

                                                                                    ⊢c E
                           WFC-Empty                     WFC-Single                              WFC-Pair
                    ⊢c ϵ                        ⊢c Ri                         ⊢c Ri : Ci : e


           Figure 10 Well-formedness rules for behaviour and cown histories.


        history of behaviour i is extended with the spawn event of the new behaviour. The Run rule
        picks a pending behaviour whose required cown set does not overlap with the cown set of
        any running behaviour, nor any behaviour before it in the queue, and adds it to the set of
        running behaviours. The history of this behaviour is initiated with the run event of that
        behaviour. Similarly, the history of each required cown is extended with the same run event.
        Finally, the Complete rule picks a running behaviour whose statement has been reduced
        to done and removes it. This releases the cowns held by the behaviour and allows pending
        behaviours with overlapping cown sets to spawn in the future. The history of the behaviour
        as well as the histories of its required cowns are extended with the completion event of that
        behaviour. Note that the semantics cannot get stuck: it is always possible to apply at least
        one of the rules until there are no more running or pending behaviours left.

        4.2    Properties of Histories
        As a program executes, the resulting history describes how that program executed. In this
        section we define properties of the histories that may be produced by the semantics in the
        previous section.
            A history consists of a set of histories for behaviours and a set of histories for cowns, each
        of which is a sequence of events. These components have their own well-formedness rules,
        shown in Figure 10. The behaviour history of behaviour i is well-formed if it has zero or
        more events, the first which is the run event of i. It is followed by zero or more spawn events
        and may end with the completion event of i. A cown history is well-formed if it consists of
        pairs of run and completion events for the same behaviour.
L. Cheeseman, E. Castegren, T. Wrigstad, S. Drossopoulou, and M. J. Parkinson                           23:11


    Since we are interested in which event happens before another, we recreate an order using
a timestamping function τ : Event → N. We use this timestamping function to formulate
the order requirements of histories.
▶ Definition 10 (Well-timed history). A history is well-timed with respect to a timestamping
function τ , written τ ⊢t H, if the following conditions are met:
(1) ∀i, e1 , e2 . H(i) = _ : e1 : e2 : _ =⇒ τ (e1 ) < τ (e2 )     Behaviour histories are ordered
(2) ∀c, e1 , e2 . H(c) = _ : e1 : e2 : _ =⇒ τ (e1 ) < τ (e2 )            Cown histories are ordered
(3) ∀i, j . Si ∈ H(j) ∧ Ri ∈ H(i) =⇒ τ (Si ) < τ (Ri )               Spawns are ordered before runs
(4) ∀c, i, j . Ci ∈ H(c) ∧ Rj ∈ H(c) ∧ τ (Ci ) < τ (Rj ) =⇒ τ (Si ) < τ (Sj )
                              Spawns over the same cowns are ordered by how they ran and completed

In a well-timed history, events in behaviour and cown histories are ordered before subsequent
events (1 and 2), spawn events are ordered before their corresponding runs (3), and spawn
events for behaviours using the same cown are ordered according to their completion and
run events (4). Note that the last timing requirement corresponds to the hbos relation in
Definition 9.
▶ Definition 11 (Well-formed history). A history is well-formed with respect to a timestamping
function, written τ ⊢ H, if the following conditions are met:
(1) ∀i . i ⊢b H(i)     (2) ∀c . ⊢c H(c)       (3) τ ⊢t H         See Figure 10 and Definition 10
(4) ∀i, j, k . j ̸= k ∧ Si ∈ H(j) =⇒ Si ∈
                                        / H(k)                              Spawn events are unique
(5) ∀c, e . e ∈ H(c) =⇒ ∃i . e ∈ H(i)         Cown history events are also in some behaviour history
(6) ∀c, i . Ri ∈ H(c) ∧ Ci ∈ H(i) =⇒ Ci ∈ H(c) Cown histories don’t miss completion events
A well-formed history combines the three previous relations (1–3) and adds three additional
requirements: the same spawn event cannot appear in multiple behaviour histories (4); each
event in a cown history corresponds to some event in a behaviour history (5); and if a
behavior ran on a cown and later completed, then the completion event appears in that
cown’s history (6).
    In order to connect the semantics to the axiomatic model we define a translation from
histories to candidate executions and show that such executions are always valid.
▶ Definition 12 (Translation to axiomatic model). A history H is translated to a model JHK
by getting the program order from adjacent events in behaviour histories and the cown order
from adjacent completion and run events in cown histories:
    JHK = (E, po , co )
      where
        E = {e | ∃i.e ∈ H(i)}
        po = {(e1 , e2 ) | ∃i.H(i) = _ : e1 : e2 : _}
        co = {(Ci , Ri , c) | H(c) = _ : Ci : Ri : _}

▶ Theorem 13 (Translation soundness). A well-formed history translates into a valid execution:
   ⊢ H =⇒ JHK valid
Proof. Most constraints of Definition 8 are straightforward properties of lists – the more
involved parts of the proof are items 8 and 9. For item 8, we prove that there is always a path
from one event in a cown history to a later, either via coc (adjacent complete/run events)
or via po∗ (the run and completion events in the same behaviour history). For item 9, we
prove acyclicity using the well-timedness in Definition 10 to show that the timestamp always
increases along the four kinds of relations. We refer to the mechanisation for details [7]. ◀



                                                                                                       CONCUR 2026
23:12    when Behaviours Have to Happen


         4.3    Soundness of Core Calculus According to the Axiomatic Model
         In the previous section, we showed that a well-formed history translates to a valid execution
         in the axiomatic model. In this section we show that the semantics is sound according the
         axiomatic model by proving that it always produces a well-formed history.
             In addition to general well-formedness, the history of an execution is going to match the
         specific configuration that it was produced together with.
         ▶ Definition 14 (Matching history). We say that a history matches a configuration, written
         H; τ ⊢ ⟨br , bp ⟩, if the following conditions are met:
         (1) |br | = |{i | (i, _, _) ∈ br }|                     Running behaviours have unique identifiers
         (2) ∀i . (i, _, _) ∈ br ⇐⇒ Ri ∈ H(i) ∧ Ci ∈
                                                   / H(i)                    Running behaviours have started
         (3) ∀(i, _, _) ∈ bp . Ri ∈
                                  / H(i)                                 Pending behaviours have not started
         (4) ∀(i, _, _) ∈ bp . ∃j . Si ∈ H(j)                          Pending behaviours have been spawned
         (5) ∀i, j . Si ∈ H(j) =⇒ (i, _, _) ∈ bp ∨ (i, _, _) ∈ br ∨ Ci ∈ H(i)
                                                  Spawned behaviours are pending, running or have completed
         (6) ∀i . Ci ∈ H(i) =⇒ (j, _, _) ∈
                                         / br ∪ bp Completed behaviours are neither running nor pending
         (7) ∀i, c . ((i, c, _) ∈ br ∧ c ∈ c) ⇐⇒ (Ri ∈ H(c) ∧ Ci ∈
                                                                 / H(c))
                                                     Cown histories reflect the cown set of running behaviours
         (8) ∀c, i . Ri ∈ H(c) =⇒ ∃j . Si ∈ H(j)            Running behaviours requiring cowns were spawned
                                    
         (9) τ (Si ) | (i, _, _) ∈ bp increasing                  The pending queue is sorted on spawn order
        (10) ∀i, j, c . Ri ∈ H(c) ∧ (j, c, _) ∈ bp ∧ c ∈ c =⇒ τ (Si ) < τ (Sj )
                                           Pending behaviours were spawned after behaviours that have started

         In a history H that matches some configuration, we have that: no two running behaviours
         share the same identifier (1); a behaviour is currently running if and only if H contains
         its run event but not its completion event (2); if a behaviour is pending then H does not
         have its start event (3) but some behaviour has its spawn event (4); if there is a spawn
         event for some behaviour in H then that behaviour is either pending, running, or its history
         has a completion event (5); if there is a completion event for some behaviour in H then
         this behaviour is neither running nor pending (6); a running behaviour is holding cowns c
         if and only if the history of each of these cowns has a run event but no completion event
         for this behaviour (7); and if a behavior ran on a cown, it must have been spawned by
         some behavior (8). The last requirement prevents out-of-thin-air behaviours, but avoids the
         chicken-and-egg problem of how the initial behaviour was spawned by allowing run events to
         exist without a corresponding spawn event as long as these behaviours do not require any
         cowns. Furthermore, the pending behaviours must be strictly increasing according to the
         timestamps of their spawns (9) and a running behaviour that holds some cown must have
         been spawned before any pending behaviour requiring the same cown (10).
             The semantics preserves both well-formed and matching histories.
         ▶ Theorem 15 (Preservation of well-formed and matching histories). Starting from a well-
         formed and matching history, evaluation produces another well-formed and matching history:

            τ ⊢ H ∧ H; τ ⊢ cfg ∧ cfg/H ⇝ cfg ′ /H ′ =⇒ ∃τ ′ . τ ′ ⊢ H ′ ∧ H ′ ; τ ′ ⊢ cfg ′

        Proof. By cases on the evaluation relation. For each case we select a τ ′ that is τ extended
        so that the new event produced by that evaluation step is given a timestamp larger than any
        previous timestamp. Preservation of each of the two relations can then be proved separately.
        We refer to the mechanisation for details [7].                                             ◀
L. Cheeseman, E. Castegren, T. Wrigstad, S. Drossopoulou, and M. J. Parkinson                              23:13


  1    when(busy, idle) { O                   1   when(src) { S      valid     1   when(src) { S
  2      val r = busy.use();                  2     when(log) { T } ⇒          2     when(log) { T }
  3      idle.use(r);             no early    3   };                           3   };
  4      when(log) { P };         release     4   when(src) { U };             4   when(src, dst) {
  5      idle.use_more();                     5   when(dst) { V };             5     U + V };
  6    };                                     6   when(dst) { W       ⇐        6   when(dst) { W
  7    when(busy) { Q                                                                when(log) { X }
                                              7     when(log) { X } invalid    7
  8      when(log) { R }                      8   }                            8   }
  9    }

(a) We can only release busy after O         (b) We can merge two behaviours, but we cannot necessarily
has spawned its last behaviour.              split a behaviour into two.

                                                   valid
                      1   when(src) { A                      1   when(dst) { C }
                                                    ⇒
                      2    when(dst) { B }                   2   when(src) { A
                      3   };                        ⇐        3    when(dst) { B }
                      4   when(dst) { C }          invalid   4   };

                    (c) We can swap two behaviours when the second (and its children)
                    do not causally depend on the first.

      Figure 11 Potential transformations of behaviours with respect to causality.


Together with Theorem 13 this proves that the semantics is sound with respect to the
axiomatic model.


 5       Discussion
The theorems in Section 4 establish that the operational semantics is sound with respect
to the axiomatic model, but not complete. This gap is not a flaw: the axiomatic model
characterises the full space of valid executions through intrinsic orders and the derived
happens-before relation, serving as a specification for implementations and optimisations
beyond what the operational semantics alone permits. We discuss two aspects: program
transformations that the model enables and how the model’s design could be extended and
refined.

5.1      Program Transformations with Respect to Causality
Like Java and C/C++, many languages use axiomatic models to capture relaxed memory
semantics and define clear optimisation boundaries. Our axiomatic model of BoC can play a
similar role: it defines optimisation boundaries within which compilers and runtimes may
optimise while preserving the causal dependencies between behaviours.

Releasing Cowns Early. One potential optimisation is to release cowns early, once they are
no longer needed, but before the completion of a behaviour. This can allow more concurrency
between behaviours that require the same cowns. Such an optimisation would be useful in
cases where a cown is heavily contended. Figure 11a shows an example where the behaviour
 O uses cowns busy and idle, and then spawns a behaviour P that uses log. Assume that

the use of the two cowns in O is such that they must appear together, but once busy has
been used, idle can be used independently. We can use the model of causality to understand
that we cannot release busy until after O has spawned P . If we were to release busy before
spawning P , then Q could run and spawn R before O has spawned P , which would



                                                                                                          CONCUR 2026
23:14   when Behaviours Have to Happen


        violate the intended causal dependencies between P and R . However, we can release busy
        after spawning P (Line 4) and before the second use of idle (Line 5), as this will not violate
        any causal dependencies. This means that early release of a cown is sound as long as the
        cown is only released after the last behaviour spawn of a behaviour holding the cown.

        Merging and Splitting Behaviours. It may also be useful to merge or split behaviours. This
        could reduce the overhead of spawning and scheduling small behaviours (for example when
        multiple behaviours require the same cowns), or to increase the granularity of concurrency.
        Merging two behaviours into one behaviour that requires the union of their cowns is always
        sound, but splitting a behaviour into two behaviours that require subsets of the original
        cowns is not always sound. Figure 11b shows an example of this imbalance. It is sound
        to merge U and V into a single behaviour that requires both src and dst, but it is not
        sound to split this merged behaviour back into two separate behaviours, as this would
        violate the causal dependencies between T and X . To split the behaviours would require a
        transformation where the behaviours are split to enable concurrency, and then followed by
        an empty behaviour that requires both cowns to preserve the causal dependencies. Note also
        that this would violate the atomicity of the original behaviour U + V .

        Reordering Behaviours. Figure 11c shows how this transformation is also asymmetric. The
        example contains two behaviours A and C that require the different cowns, and B which is
        spawned by A and requires the same cowns as C . We can swap the order of A and C from
        left to right without violating the causal dependencies. This will induce a new happens-before
        edge between C and B , but the executions before and after the transformation will still
        be valid. However, we cannot swap the order of A and C from right to left, as this would
        violate the causal dependency between C and B : this transformation would allow B to be
        spawned and run before C has completed.

        5.2    Refining the Axiomatic Model
        The model we have introduced in this paper defines the causal dependencies between
        behaviours. We can use these guarantees to further understand the outcomes of a program,
        for example, to understand cown read and writes. To model these cown operations explicitly,
        we could add corresponding events and constrain the causal relations of these access events
        from the existing behaviour relations. For example, we could require that each read observes
        the most recent write in happens-before order.
            In this paper, we assume that all behaviours can both read and write the cowns they
        require. This is the model used in prior BoC work, but richer access modes are possible. For
        example, some behaviours could require a cown only for reading, while others require it for
        writing. This would permit finer-grained concurrency: read-only behaviours on the same
        cown could run concurrently, while writers would still require exclusive access. The model
        could capture this either by relaxing the cown-order axioms to allow fan-out and fan-in, or
        by enriching the cown order with access mode information. In either case, cown events must
        remain consistent with each behaviour’s declared access mode.

         6     Related Work
        Memory Models. Memory models are often defined axiomatically, and they have been used
        to define the relaxed behaviour of concurrent programs on modern hardware architectures
        and programming languages [14, 2, 17]. These models are similar to our axiomatic model in
L. Cheeseman, E. Castegren, T. Wrigstad, S. Drossopoulou, and M. J. Parkinson                         23:15


that they define a set of events and relations between them, and they specify the allowed
executions of a concurrent program. Our model is not focused on memory consistency, but
rather on the causal dependencies between behaviours in a concurrent program. Because
BoC requires isolation of cowns, the coherence order and reads-from employed in traditional
memory models are derivable from the program order and the cown order (cf. Section 5.2).


Actor Model Programming. The Actor model is a well-known paradigm [11, 1], widely
implemented in practical actor runtimes [3, 19]. Its operational presentation is natural
because the original model has no explicit inter-behaviour or inter-actor causal dependencies.
Some implementations of actor models do provide mechanisms or guarantees for causal
consistency and ordering behaviours [21, 20]. In earlier work, we compared actors with
BoC and showed that BoC decouples isolation from concurrency, enabling more expressive
synchronisation [9] This decoupling also introduces richer inter-behaviour causal dependencies,
which are better captured in an axiomatic style than in a purely operational one, where these
dependencies must be encoded directly in the semantic rules.


Causal Consistency in Distributed Systems. Causal consistency is a well-known consistency
model in distributed systems, ensuring that operations with causal relationships are observed
in the same order by all processes; it is classically defined using a happens-before relation [15]
and formalised in modern treatments of causal consistency for shared objects [18]. This
resembles our derived happens-before relation in that both capture causal dependencies
between events.


Consistency Models for Databases. Work on consistency models for databases uses axio-
matic models to characterise the visibility of updates between transactions [8]. These models
often abstract the nested structure of transactions, treating them as flat, atomic units. While
BoC is also concerned with the visibility of updates, the program structure and nesting of
behaviours are intrinsic to ordering and causality.


Deterministic Shared-memory Concurrency. Shared-memory deterministic concurrency
models, such as Deterministic Parallel Java [5, 6] and Deterministic Threads [16], have been
proposed to provide deterministic behaviour in concurrent programs. They typically enforce
determinism through combinations of static analysis and runtime checking of shared-memory
accesses. By contrast, BoC does not target full determinism nor expect shared memory; it
provides a causality-oriented account of concurrent behaviours accessing isolated resources,
grounded in dynamic execution.


 7     Conclusion

In this paper, we presented an axiomatic model for BoC that captures the intended causal
dependencies between behaviours. Using representative example programs and executions,
we motivated the model design and showed how the derived happens-before relation separates
intrinsic causality from incidental operational ordering. We then established that operational
semantics presented in earlier work is sound with respect to this model via a representative core
calculus. Taken together, these results provide an implementation-independent foundation
for reasoning about BoC causality, while enabling more permissive yet valid executions to be
recovered through scheduling and compilation.




                                                                                                     CONCUR 2026
23:16   when Behaviours Have to Happen


             References
         1   Gul Agha. Actors: A Model of Concurrent Computation in Distributed Systems. The MIT
             Press, December 1986. doi:10.7551/mitpress/1086.001.0001.
         2   Jade Alglave, Luc Maranget, and Michael Tautschnig. Herding cats: Modelling, simulation,
             testing, and data mining for weak memory. ACM Trans. Program. Lang. Syst., 36(2), July
             2014. doi:10.1145/2627752.
         3   Joe Armstrong. Concurrent Programming in ERLANG. Pearson Education. Prentice Hall,
             1996. URL: https://books.google.se/books?id=EqZQAAAAMAAJ.
         4   Ellen Arvidsson, Elias Castegren, Sylvan Clebsch, Sophia Drossopoulou, James Noble, Mat-
             thew J. Parkinson, and Tobias Wrigstad. Reference capabilities for flexible memory manage-
             ment. Proc. ACM Program. Lang., 7(OOPSLA2), October 2023. doi:10.1145/3622846.
         5   Robert L Bocchino, Vikram Adve, Sarita Adve, and Marc Snir. Parallel programming must
             be deterministic by default. Usenix HotPar, 6(10.5555):1855591–1855595, 2009.
         6   Robert L. Bocchino, Vikram S. Adve, Danny Dig, Sarita V. Adve, Stephen Heumann, Rakesh
             Komuravelli, Jeffrey Overbey, Patrick Simmons, Hyojin Sung, and Mohsen Vakilian. A
             type and effect system for deterministic parallel java. In Proceedings of the 24th ACM
             SIGPLAN Conference on Object Oriented Programming Systems Languages and Applications,
             OOPSLA ’09, pages 97–116, New York, NY, USA, 2009. Association for Computing Machinery.
             doi:10.1145/1640089.1640097.
         7   Elias    Castegren     and     Luke     Cheeseman.              A     mechanised      axiomatic
             model     for    behaviour-oriented     concurrency,       2026.           Software,     swhId:
             swh:1:dir:24350cf7167ab1b9d00f8a2d64cc3fe32dfb4560 (visited on 2026-08-13). URL:
             https://github.com/fxpl/axiomatic_boc, doi:10.4230/artifacts.27655.
         8   Andrea Cerone, Giovanni Bernardi, and Alexey Gotsman. A Framework for Transactional
             Consistency Models with Atomic Visibility. In Luca Aceto and David de Frutos Escrig, editors,
             26th International Conference on Concurrency Theory (CONCUR 2015), volume 42 of Leibniz
             International Proceedings in Informatics (LIPIcs), pages 58–71, Dagstuhl, Germany, 2015.
             Schloss Dagstuhl – Leibniz-Zentrum für Informatik. doi:10.4230/LIPIcs.CONCUR.2015.58.
         9   Luke Cheeseman, Elias Castegren, Sophia Drossopoulou, Tobias Wrigstad, Sylvan Clebsch,
             and Matthew Parkinson. Decoupling Isolation and Concurrency: An Actor-Centric View
             of Behaviour-Oriented Concurrency, pages 165–186. Springer Nature Switzerland, Cham, 2026.
             doi:10.1007/978-3-032-05291-9_7.
        10   Luke Cheeseman, Matthew J. Parkinson, Sylvan Clebsch, Marios Kogias, Sophia Drossopoulou,
             David Chisnall, Tobias Wrigstad, and Paul Liétar. When concurrency matters: Behaviour-
             oriented concurrency. Proc. ACM Program. Lang., 7(OOPSLA2), October 2023. doi:10.1145/
             3622852.
        11   Carl Hewitt, Peter Bishop, and Richard Steiger. Session 8 formalisms for artificial intelligence
             a universal modular actor formalism for artificial intelligence. In Advance papers of the
             conference, volume 3, page 235. Stanford Research Institute Menlo Park, CA, 1973.
        12   Matthew Johnson. Explorations into a programming model for BoC in the Python runtime.
             https://github.com/matajoh/pyrona, 2025. Accessed February 2025.
        13   Matthew Johnson, Matt Parkinson, Sylvan Clebsch, Fridtjof Stoldt, and Tobias Wrigstad.
             Research programming language for concurrent ownership. https://pep-previews--4468.
             org.readthedocs.build/pep-0795/, 2025. Accessed December 2025.
        14   ISO/IEC JTC1/SC22/WG14. Programming languages — C. Technical Report ISO/IEC
             9899:2011, International Organization for Standardization, 2011. Section 6.2.4.
        15   Leslie Lamport. Time, clocks, and the ordering of events in a distributed system, pages 179–196.
             Association for Computing Machinery, New York, NY, USA, 2019. doi:10.1145/3335772.
             3335934.
        16   Tongping Liu, Charlie Curtsinger, and Emery D. Berger. Dthreads: efficient deterministic
             multithreading. In Proceedings of the Twenty-Third ACM Symposium on Operating Systems
L. Cheeseman, E. Castegren, T. Wrigstad, S. Drossopoulou, and M. J. Parkinson                         23:17


     Principles, SOSP ’11, pages 327–336, New York, NY, USA, 2011. Association for Computing
     Machinery. doi:10.1145/2043556.2043587.
17   Jeremy Manson, William Pugh, and Sarita V. Adve. The java memory model. In Proceedings
     of the 32nd ACM SIGPLAN-SIGACT Symposium on Principles of Programming Languages,
     POPL ’05, pages 378–391, New York, NY, USA, 2005. Association for Computing Machinery.
     doi:10.1145/1040305.1040336.
18   Matthieu Perrin, Achour Mostefaoui, and Claude Jard. Causal consistency: beyond memory.
     In Proceedings of the 21st ACM SIGPLAN Symposium on Principles and Practice of Parallel
     Programming, pages 1–12, 2016. doi:10.1145/2851141.2851170.
19   Akka Team. Akka: A toolkit for building concurrent, distributed, and resilient message-driven
     applications on the jvm. https://akka.io/, 2025. Accessed March 2025.
20   Pony Team. Pony: A capabilities-secure, actor-model, high-performance programming language.
     https://www.ponylang.io/, 2025. Accessed March 2025.
21   Carlos Varela and Gul Agha. Programming dynamically reconfigurable open systems with
     salsa. ACM SIGPLAN Notices, 36(12):20–34, 2001. doi:10.1145/583960.583964.
22   Tobias Wrigstad. Pyerlang: A stepping stone towards behaviour-oriented concurrency in
     python (keynote). In Proceedings of the 24th ACM SIGPLAN International Workshop on
     Erlang, Erlang ’25, page 1, New York, NY, USA, 2025. Association for Computing Machinery.
     doi:10.1145/3759161.3771262.




                                                                                                     CONCUR 2026

