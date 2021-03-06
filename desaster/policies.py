# -*- coding: utf-8 -*-
"""
Module of classes that implement compound policies for custom arrangements of
DESaster recovery programs.

Classes:
RecoveryPolicy
Insurance_IA_Loan_Sequential

@author: Scott Miles (milessb@uw.edu), Meg Longman
"""

class RecoveryPolicy(object):
    def __init__(self, env, stage):
        self.env = env
        self.level = stage
    def policy(self):
        pass

class Funding_Search_Sequential(RecoveryPolicy):
    def _init_(self,env,stage):
        RecoveryPolicy._init_(self,env)
        self.level = stage
    def policy(self, insurance_program, nra_program, loan_program, entity):
        """A process (generator) representing entity search for money to rebuild or
        repair home based on requests for insurance and/or NRA aid and/or loan.

        env -- Pointer to SimPy env environment.
        entity -- A single entities object, such as Household().
        financial_capital -- A structures.FinancialCapital() object.
        human_capital -- A structures.HumanCapital() object.
        write_story -- Boolean indicating whether to track a entitys story.

        Returns or Attribute Changes:
        entity.story -- Process outcomes appended to story.
        money_search_start -- Record time money search starts
        entity.money_to_rebuild -- Technically changed (increased) by functions
                                    called within.
        """


        money_search_start = self.env.now

    # if household can afford rebuild themselves - how does this work in installments?
    # in reality, very unlikely
        if (entity.money_to_rebuild >= entity.property.damage_value
            and entity.insurance == 0.0):

            # If True, append search outcome to story.
            if entity.write_story:
                entity.story.append(
                    '{0} already had enough money to rebuild (1:,.0f) and did not seek assistance. '.format(
                                        entity.name.title(),
                                        entity.money_to_rebuild
                                        )
                )
            return

# if using, insert insurance program here

        # gives cost of repair for each section
        if self.level == 'Up to Plinth Level':
            cost = entity.property.plinth_value
        elif self.level == 'Superstructure':
            cost = entity.property.wall_value
        elif self.level == 'Roofing':
            cost = entity.property.roof_value

        # household applies to NRA for funding   
        if entity.money_to_rebuild < cost:            
            try_nra = self.env.process(nra_program.process(entity))
            
            money_search_outcome = yield try_nra

#process automatically adds to entity.money_to_rebuild
        if entity.money_to_rebuild < cost:            
            try_loan = self.env.process(loan_program.process(entity))
            
            money_search_outcome = yield try_loan

#ignoring patience issues for the moment (in reality, this causes people to start building)
        search_duration = self.env.now - money_search_start


                  
        if self.level == 'Up to Plinth Level':
            if entity.money_to_rebuild < entity.property.plinth_value:
            # If write_story is True, then append money search outcome to entity's story.
                if entity.write_story:
                    entity.story.append(
                        'It took {0} {1:.0f} days to exhaust financial assistance options but still does not have enough money to rebuild to plinth level (Rs{2:.0f}). '.format(
                            entity.name.title(),
                            search_duration,
                            entity.money_to_rebuild
                            )
                    )
            return
        elif self.level == 'Superstructure':
            if entity.money_to_rebuild < entity.property.wall_value:
            # If write_story is True, then append money search outcome to entity's story.
                if entity.write_story:
                    entity.story.append(
                        'It took {0} {1:.0f} days to exhaust financial assistance options but still does not have enough money to rebuild to wall level (Rs{2:.0f}). '.format(
                            entity.name.title(),
                            search_duration,
                            entity.money_to_rebuild
                            )
                    )
            return
        elif self.level == 'Roofing':
            if entity.money_to_rebuild < entity.property.roof_value:
            # If write_story is True, then append money search outcome to entity's story.
                if entity.write_story:
                    entity.story.append(
                        'It took {0} {1:.0f} days to exhaust financial assistance options but still does not have enough money to rebuild roof (Rs{2:.0f}). '.format(
                            entity.name.title(),
                            search_duration,
                            entity.money_to_rebuild
                            )
                    )
            return
#entity completes search and has sufficient funding
        if entity.write_story:
            entity.story.append(
                'It took {0} {1:.0f} days to exhaust financial assistance options and now has Rs{2:,.0f} for repairs. '.format(
                        entity.name.title(),
                        search_duration,
                        entity.money_to_rebuild
                        )
                )
            return
        
        
        
class Insurance_IA_Loan_Sequential(RecoveryPolicy):
    def __init__(self, env):
        RecoveryPolicy.__init__(self, env)
    def policy(self, insurance_program, fema_program, loan_program, entity,
                        search_patience):
        """ **Original Desaster process (generator) representing entity search for money to rebuild or
        repair home based on requests for insurance and/or FEMA aid and/or loan. Kept in for reference if NRA processes need to be updated (eg insurance added in) at a later date**

        env -- Pointer to SimPy env environment.
        entity -- A single entities object, such as Household().
        search_patience -- The search duration in which the entity is willing to
                            wait to find a new home. Does not include the process of
                            securing money.
        financial_capital -- A structures.FinancialCapital() object.
        human_capital -- A structures.HumanCapital() object.
        write_story -- Boolean indicating whether to track a entitys story.

        Returns or Attribute Changes:
        entity.story -- Process outcomes appended to story.
        money_search_start -- Record time money search starts
        entity.gave_up_funding_search -- Record time money search stops
        entity.money_to_rebuild -- Technically changed (increased) by functions
                                    called within.
        """

        # Record when money search starts
        # Calculate the time that money search patience ends
        money_search_start = self.env.now
        patience_end = money_search_start + search_patience

        # Return out of function if entity has enough money to rebuild and does not
        # have any insurance coverage.
        if (entity.money_to_rebuild >= entity.property.damage_value
            and entity.insurance == 0.0):

            # If True, append search outcome to story.
            if entity.write_story:
                entity.story.append(
                    '{0} already had enough money to rebuild (1:,.0f) and did not seek assistance. '.format(
                                        entity.name.title(),
                                        entity.money_to_rebuild
                                        )
                                    )
            return

        # If entity has insurance then yield an insurance claim request, the duration
        # of which is limited by entity's money search patience.
        if entity.insurance > 0.0:

            # Define a timeout process to represent search patience, with duration
            # equal to the *remaining* patience. Pass the value "Gave up" if the
            # process completes.
            find_search_patience = self.env.timeout(
                                                        patience_end - self.env.now,
                                                        value='Gave up'
                                                    )

            # Define insurance claim request process. Pass data about available
            # insurance claim adjusters.
            try_insurance = self.env.process(insurance_program.process(entity))

            # Yield both the patience timeout and the insurance claim request.
            # Pass result for the process that completes first.
            money_search_outcome = yield find_search_patience | try_insurance

            # If patience process completes first, interrupt the insurance claim
            # request and return out of function.
            if money_search_outcome == {find_search_patience: 'Gave up'}:
                if try_insurance.is_alive:
                    entity.gave_up_funding_search = self.env.now
                    try_insurance.interrupt(entity.gave_up_funding_search - money_search_start)
                    return
                else:
                    entity.gave_up_funding_search = self.env.now
                    return

        # If entity (still) does not have enough rebuild money then yield a FEMA IA
        # request, the duration of which is limited by entity's money search patience.
        if entity.money_to_rebuild < entity.property.damage_value:

            # Define a timeout process to represent search patience, with duration
            # equal to the *remaining* patience. Pass the value "Gave up" if the
            # process completes.
            find_search_patience = self.env.timeout(
                                                    patience_end - self.env.now,
                                                    value='Gave up'
                                                    )

            # Define FEMA aid request process. Pass data about available
            # FEMA processors, budget, and maximum grant amount.
            try_fema = self.env.process(fema_program.process(entity))

            # Yield both the patience timeout and the FEMA aid request.
            # Pass result for the process that completes first.
            money_search_outcome = yield find_search_patience | try_fema

            # If patience process completes first, interrupt the FEMA aid
            # request and return out of function.
            if money_search_outcome == {find_search_patience: 'Gave up'}:
                if try_fema.is_alive:
                    entity.gave_up_funding_search = self.env.now
                    try_fema.interrupt(entity.gave_up_funding_search - money_search_start)
                    return
                else:
                    entity.gave_up_funding_search = self.env.now

        # If entity (still) does not have enough rebuild money then yield a loan
        # request, the duration of which is limited by entity's money search patience.
        if entity.money_to_rebuild < entity.property.damage_value:

            # Define a timeout process to represent search patience, with duration
            # equal to the *remaining* patience. Pass the value "Gave up" if the
            # process completes.
            find_search_patience = self.env.timeout(patience_end - self.env.now,
                                    value='Gave up')

            # Define loan request process. Pass data about available
            # loan processors.
            try_loan = self.env.process(loan_program.process(entity))

            # Yield both the patience timeout and the loan request.
            # Pass result for the process that completes first.
            money_search_outcome = yield find_search_patience | try_loan

            # If patience process completes first, interrupt the loan
            # request and return out of function.
            if money_search_outcome == {find_search_patience: 'Gave up'}:
                if try_loan.is_alive:
                    entity.gave_up_funding_search = self.env.now
                    try_loan.interrupt(entity.gave_up_funding_search - money_search_start)
                    return
                else:
                    entity.gave_up_funding_search = self.env.now

        # Record the time and duration when entity's search for money ends without
        # giving up.
        search_duration = self.env.now - money_search_start

        # If entity (STILL) does not have enough rebuild money then indicate so and
        # that options have been exhausted.
        if entity.money_to_rebuild < entity.property.damage_value:
            # If write_story is True, then append money search outcome to entity's story.
            if entity.write_story:
                entity.story.append(
                    'It took {0} {1:.0f} days to exhaust financial assistance options but still does not have enough money to cover repairs (${2:,.0f}). '.format(
                            entity.name.title(),
                            search_duration,
                            entity.money_to_rebuild
                            )
                    )
            return

        # If entity completed search and obtained sufficient funding.
        # If write_story is True, then append money search outcome to entity's story.
        if entity.write_story:
            entity.story.append(
                'It took {0} {1:.0f} days to exhaust financial assistance options and now has ${2:,.0f} for repairs. '.format(
                        entity.name.title(),
                        search_duration,
                        entity.money_to_rebuild
                        )
                )
